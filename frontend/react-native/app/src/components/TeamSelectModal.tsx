import React, { useState, useRef } from 'react';
import { View, Text, Modal, TouchableOpacity, StyleSheet, Animated, Dimensions, Image, ScrollView, Pressable } from 'react-native';
import styled from 'styled-components/native';
import { getAdjustedWidth } from '../constants/layout';
import { useTeam } from '../context/TeamContext';
import { useJoin } from '../context/JoinContext';
import { teamColors } from '../styles/teamColors';
import { useNavigation } from '@react-navigation/native';

// 팀 이름과 코드 매핑
const teamNameToCode: { [key: string]: keyof typeof teamColors } = {
  "KIA 타이거즈": "KIA",
  "삼성 라이온즈": "SAMSUNG",
  "LG 트윈스": "LG",
  "두산 베어스": "DOOSAN",
  "KT 위즈": "KT",
  "SSG 랜더스": "SSG",
  "롯데 자이언츠": "LOTTE",
  "한화 이글스": "Hanwha",
  "NC 다이노스": "NC",
  "키움 히어로즈": "Kiwoom",
};

interface TeamSelectModalProps {
  visible: boolean;
  onClose: () => void;
  onSelectTeam: (team: string) => void;
  width: number;
}

const teams = [
  { id: 1, name: 'KIA 타이거즈', logo: require('../../assets/kbo/tigers.png') },
  { id: 2, name: '삼성 라이온즈', logo: require('../../assets/kbo/lions.png') },
  { id: 3, name: 'LG 트윈스', logo: require('../../assets/kbo/twins.png') },
  { id: 4, name: '두산 베어스', logo: require('../../assets/kbo/bears.png') },
  { id: 5, name: 'KT 위즈', logo: require('../../assets/kbo/wiz.png') },
  { id: 6, name: 'SSG 랜더스', logo: require('../../assets/kbo/landers.png') },
  { id: 7, name: '롯데 자이언츠', logo: require('../../assets/kbo/giants.png') },
  { id: 8, name: '한화 이글스', logo: require('../../assets/kbo/eagles.png') },
  { id: 9, name: 'NC 다이노스', logo: require('../../assets/kbo/dinos.png') },
  { id: 10, name: '키움 히어로즈', logo: require('../../assets/kbo/heroes.png') },
];

interface ButtonProps {
  isSelected: boolean;
  teamColor?: string;
}

interface StyledProps {
  width: number;
}

const ModalContainer = styled(Animated.View)<StyledProps>`
  position: absolute;
  bottom: 0;
  left: ${props => (Dimensions.get('window').width - props.width) / 2}px;
  width: ${props => props.width}px;
  background-color: white;
  border-top-left-radius: 24px;
  border-top-right-radius: 24px;
  padding: 20px;
  padding-bottom: 32px;
  shadow-color: #000;
  shadow-offset: 0px -2px;
  shadow-opacity: 0.1;
  shadow-radius: 8px;
  elevation: 5;
  max-height: 92%;
`;

const Header = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const Title = styled.Text`
  font-size: 20px;
  font-weight: bold;
  color: #1B1D1F;
`;

const CloseButton = styled.TouchableOpacity`
  padding: 8px;
`;

const TeamGrid = styled.View`
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: space-between;
  padding-horizontal: 4px;
  margin-top: 8px;
`;

const TeamButton = styled.TouchableOpacity<ButtonProps>`
  width: 48%;
  background-color: ${props => props.isSelected ? `${props.teamColor}10` : '#fff'};
  border-radius: 12px;
  padding: 16px 12px;
  align-items: center;
  margin-bottom: 12px;
  elevation: ${props => props.isSelected ? 2 : 1};
  shadow-color: ${props => props.isSelected ? props.teamColor || '#2D5BFF' : '#000'};
  shadow-offset: 0px 2px;
  shadow-opacity: ${props => props.isSelected ? 0.12 : 0.08};
  shadow-radius: 8px;
  transform: scale(${props => props.isSelected ? 1 : 0.98});
`;

const TeamLogo = styled.Image`
  width: 52px;
  height: 52px;
  margin-bottom: 8px;
`;

const TeamName = styled.Text<{ isSelected: boolean }>`
  font-size: 15px;
  color: ${props => props.isSelected ? '#1B1D1F' : '#1B1D1F'};
  font-weight: ${props => props.isSelected ? '700' : '600'};
`;

const Backdrop = styled.Pressable`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
`;

const SelectButton = styled.TouchableOpacity<{ teamColor?: string }>`
  background-color: ${props => props.teamColor || '#E5E5E5'};
  padding: 16px;
  border-radius: 12px;
  align-items: center;
  margin-top: 16px;
  elevation: 3;
  shadow-color: ${props => props.teamColor || '#000'};
  shadow-offset: 0px 4px;
  shadow-opacity: 0.15;
  shadow-radius: 8px;
`;

const SelectButtonText = styled.Text`
  color: #fff;
  font-size: 18px;
  font-weight: 900;
`;

const TeamSelectModal: React.FC<TeamSelectModalProps> = ({ visible, onClose, onSelectTeam, width }) => {
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
  const { setTeamData } = useTeam();
  const { updateTeam } = useJoin();
  const navigation = useNavigation();
  const slideAnim = useRef(new Animated.Value(0)).current;
  const { height } = Dimensions.get('window');

  // 선택된 팀의 색상 가져오기
  const getSelectedTeamColor = () => {
    if (!selectedTeamId) return null;
    const selectedTeamData = teams.find(team => team.id === selectedTeamId);
    if (!selectedTeamData) return null;
    
    const teamCode = teamNameToCode[selectedTeamData.name];
    return teamCode ? teamColors[teamCode].primary : null;
  };

  React.useEffect(() => {
    if (visible) {
      Animated.spring(slideAnim, {
        toValue: 1,
        tension: 65,
        friction: 11,
        useNativeDriver: true,
      }).start();
    } else {
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }).start();
      setSelectedTeamId(null);
    }
  }, [visible]);

  const handleTeamSelect = (teamId: number) => {
    setSelectedTeamId(teamId);
  };

  const handleConfirm = () => {
    if (selectedTeamId) {
      const selectedTeamData = teams.find(team => team.id === selectedTeamId);
      if (selectedTeamData) {
        const teamCode = teamNameToCode[selectedTeamData.name];
        if (teamCode) {
          setTeamData({
            team_id: selectedTeamId,
            team_name: selectedTeamData.name,
            team_color: teamColors[teamCode].primary,
            team_color_secondary: teamColors[teamCode].secondary,
            team_color_background: teamColors[teamCode].background
          });
          updateTeam({
            id: selectedTeamId,
            name: selectedTeamData.name,
            colors: teamColors[teamCode],
            logo: selectedTeamData.logo
          });
          onSelectTeam(selectedTeamData.name);
          onClose();
          navigation.navigate('PlayerSelect' as never);
        }
      }
    }
  };

  const translateY = slideAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [height, 0],
  });

  const selectedTeamColor = getSelectedTeamColor();

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <Backdrop onPress={onClose} />
      <ModalContainer width={width} style={{ transform: [{ translateY }] }}>
        <Header>
          <Title>응원팀 선택</Title>
          <CloseButton onPress={onClose}>
            <Text style={{ fontSize: 24, color: '#666' }}>×</Text>
          </CloseButton>
        </Header>
        <ScrollView showsVerticalScrollIndicator={false}>
          <TeamGrid>
            {teams.map((team) => {
              const isSelected = selectedTeamId === team.id;
              const teamCode = teamNameToCode[team.name];
              const teamColor = teamCode ? teamColors[teamCode].primary : undefined;

              return (
                <TeamButton
                  key={team.id}
                  onPress={() => handleTeamSelect(team.id)}
                  activeOpacity={0.9}
                  isSelected={isSelected}
                  teamColor={teamColor}
                >
                  <TeamLogo source={team.logo} resizeMode="contain" />
                  <TeamName isSelected={isSelected}>{team.name}</TeamName>
                </TeamButton>
              );
            })}
          </TeamGrid>
          <SelectButton 
            onPress={handleConfirm} 
            disabled={!selectedTeamId}
            teamColor={selectedTeamColor || undefined}
          >
            <SelectButtonText>선택하기</SelectButtonText>
          </SelectButton>
        </ScrollView>
      </ModalContainer>
    </Modal>
  );
};

export default TeamSelectModal; 
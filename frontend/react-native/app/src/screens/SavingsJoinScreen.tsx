import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, SafeAreaView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

type RootStackParamList = {
  Home: undefined;
  Login: undefined;
  SavingsJoin: undefined;
};

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

const SavingsJoinScreen = () => {
  const navigation = useNavigation<NavigationProp>();

  return (
    <SafeAreaView style={styles.container}>
      {/* 헤더 영역 */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="chevron-back" size={24} color="black" />
        </TouchableOpacity>
      </View>

      {/* 메인 컨텐츠 */}
      <View style={styles.content}>
        <Text style={styles.title}>야금야금</Text>
        <View style={styles.rateContainer}>
          <Text style={styles.rateText}>기본 2.00% (최대 4.00%)</Text>
        </View>

        {/* 캐릭터 이미지 영역 */}
        <View style={styles.imageContainer}>
          <Image 
            source={require('../../assets/squirrel.png')} 
            style={styles.characterImage}
          />
        </View>

        {/* 상품 안내 */}
        <View style={styles.infoContainer}>
          <Text style={styles.infoTitle}>상품 안내</Text>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>상품명</Text>
            <Text style={styles.infoValue}>KBO 자유 적금 아금아금</Text>
          </View>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>계약기간</Text>
            <Text style={styles.infoValue}>12개월</Text>
          </View>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>금리</Text>
            <Text style={styles.infoValue}>기본 2.00% (최대 4.00%)</Text>
          </View>
        </View>

        {/* 가입하기 버튼 */}
        <TouchableOpacity 
          style={styles.joinButton}
          onPress={() => {/* 다음 단계로 이동 */}}
        >
          <Text style={styles.joinButtonText}>가입하기</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    height: 56,
    justifyContent: 'center',
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  backButton: {
    padding: 8,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 24,
    marginBottom: 16,
  },
  rateContainer: {
    marginBottom: 24,
  },
  rateText: {
    fontSize: 16,
    color: '#666',
  },
  imageContainer: {
    alignItems: 'center',
    marginVertical: 32,
  },
  characterImage: {
    width: 200,
    height: 200,
    resizeMode: 'contain',
  },
  infoContainer: {
    marginTop: 24,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  infoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  infoLabel: {
    color: '#666',
  },
  infoValue: {
    color: '#333',
  },
  joinButton: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 32,
    marginBottom: 24,
  },
  joinButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default SavingsJoinScreen; 
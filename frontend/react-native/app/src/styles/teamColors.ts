// src/styles/teamColors.ts
export const teamColors = {
  KIA: {
    primary: "#e30613",
    secondary: "#000000",
    background: "#ffffff",
  },
  DOOSAN: {
    primary: "#131230",
    secondary: "#CD0320",
    background: "#ffffff",
  },
  LG: {
    primary: "#C30452",
    secondary: "#000000",
    background: "#ffffff",
  },
  SAMSUNG: {
    primary: "#1428A0",
    secondary: "#ffffff",
    background: "#E10600",
  },
  KT: {
    primary: "#000000",
    secondary: "#E10600",
    background: "#FFB81C",
  },
  SSG: {
    primary: "#E10600",
    secondary: "#ffffff",
    background: "#FFB81C",
  },
  LOTTE: {
    primary: "#002B70",
    secondary: "#E10600",
    background: "#ffffff",
  },
  Hanwha: {
    primary: "#FF6600",
    secondary: "#003057",
    background: "#ffffff",
  },
  NC: {
    primary: "#1E4D92",
    secondary: "#FFB81C",
    background: "#73C8F0",
  },
  Kiwoom: {
    primary: "#6A0E21",
    secondary: "#ffffff",
    background: "#FFCCCB",
  },
};

// DB의 팀 ID를 팀 코드로 매핑
export const teamIdToCode: { [key: number]: keyof typeof teamColors } = {
  1: "KIA",
  2: "SAMSUNG",
  3: "LG",
  4: "DOOSAN",
  5: "KT",
  6: "SSG",
  7: "LOTTE",
  8: "Hanwha",
  9: "NC",
  10: "Kiwoom",
};

// DB의 팀 이름을 팀 코드로 매핑
export const teamNameToCode: { [key: string]: keyof typeof teamColors } = {
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

// 기본값 설정
export const defaultTeam = "NC";

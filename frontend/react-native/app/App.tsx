import React from 'react';
import { StyleSheet, Text, View, Button } from 'react-native';
import { useAppStore } from './src/store/useStore';

export default function App() {
  const { count, increment, decrement, reset } = useAppStore();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>React Native + TypeScript + Zustand</Text>
      <Text style={styles.counter}>Count: {count}</Text>
      <View style={styles.buttonContainer}>
        <Button title="+" onPress={increment} />
        <Button title="-" onPress={decrement} />
        <Button title="Reset" onPress={reset} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  counter: {
    fontSize: 24,
    marginBottom: 20,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '60%',
  },
});
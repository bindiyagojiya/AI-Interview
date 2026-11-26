import React from "react";
import { View, StyleSheet, Text } from "react-native";
import { Colors } from "../constants/colors";

interface ProgressBarProps {
  current: number;
  total: number;
  showText?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  current,
  total,
  showText = true,
}) => {
  const progressPercent = Math.min(100, Math.max(0, (current / total) * 100));

  return (
    <View style={styles.container}>
      {showText && (
        <View style={styles.textRow}>
          <Text style={styles.label}>Interview Progress</Text>
          <Text style={styles.counter}>
            {current} of {total}
          </Text>
        </View>
      )}
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${progressPercent}%` }]} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 12,
  },
  textRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 6,
  },
  label: {
    fontSize: 13,
    fontWeight: "500",
    color: Colors.textSecondary,
  },
  counter: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.primary,
  },
  track: {
    height: 8,
    backgroundColor: Colors.surface,
    borderRadius: 4,
    overflow: "hidden",
  },
  fill: {
    height: "100%",
    backgroundColor: Colors.primary,
    borderRadius: 4,
  },
});


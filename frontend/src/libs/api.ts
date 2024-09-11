import { dbTestCaseToDomain, dbTestLogToDomain } from "@/utils/conversion";
import { TestCase, TestLogItem } from "@/types";

export const fetchTestCases = async (): Promise<TestCase[]> => {
  try {
    const response = await fetch("/api/test-cases")
      .then((response) => response.json())
      .then((response) => response.data.map(dbTestCaseToDomain) as TestCase[]);
    return response;
  } catch (err) {
    throw err;
  }
};

export const fetchTestLogs = async (
  selectedIndex: number
): Promise<TestLogItem[]> => {
  try {
    const response = await fetch(`/api/test-logs/${selectedIndex}`)
      .then((res) => res.json())
      .then((res) => res.data.map(dbTestLogToDomain) as TestLogItem[]);
    return response;
  } catch (err) {
    throw err;
  }
};

export const triggerTest = async (selectedIndex: number): Promise<void> => {
  try {
    await fetch(`/api/trigger-tests/${selectedIndex}`);
  } catch (err) {
    throw err;
  }
};

export const resetTests = async (): Promise<void> => {
  try {
    await fetch("/api/test-reset-all");
  } catch (err) {
    throw err;
  }
};

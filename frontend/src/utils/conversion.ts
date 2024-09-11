import { TestCase, TestLogItem, TestLogType, TestStatus } from "@/types";

interface DbTestCase {
  id: number;
  description: string;
  status: TestStatus;
  no_of_steps: number;
}

interface DbTestLog {
  message: string;
  created_at: string;
  type: string;
}

export const dbTestCaseToDomain = (dbTestCase: DbTestCase) => {
  return {
    ...dbTestCase,
    noOfSteps: dbTestCase.no_of_steps,
  } as TestCase;
};

export const dbTestLogToDomain = (dbTestLog: DbTestLog) => {
  return {
    ...dbTestLog,
    createdAt: new Date(dbTestLog.created_at),
    type: dbTestLog.type as TestLogType,
  } as TestLogItem;
};

import { SVGProps } from "react";

export type IconSvgProps = SVGProps<SVGSVGElement> & {
  size?: number;
};

export type TestStatus = "todo" | "in-progress" | "success" | "failed";

export interface TestCase {
  id: string | number;
  description: string;
  noOfSteps: number;
  status: TestStatus;
}

export type TestLogType = "error" | "info";

export interface TestLogItem {
  message: string;
  createdAt: Date;
  type: TestLogType;
}

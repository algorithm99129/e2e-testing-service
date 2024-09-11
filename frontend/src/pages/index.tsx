import { useCallback, useEffect, useMemo, useState } from "react";
import { Button } from "@nextui-org/button";
import {
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Spinner,
} from "@nextui-org/react";
import { FaArrowRotateRight, FaMinus, FaPlay, FaPlus } from "react-icons/fa6";

import TestTable from "@/components/TestTable/TestTable";
import { ThemeSwitch } from "@/components/theme-switch";
import DefaultLayout from "@/layouts/default";
import {
  fetchTestCases,
  fetchTestLogs,
  resetTests,
  triggerTest,
} from "@/libs/api";
import { TestCase, TestLogItem } from "@/types";

let intervalId: NodeJS.Timeout;

export default function IndexPage() {
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set([]));
  const [cases, setCases] = useState<TestCase[]>([]);
  const [logs, setLogs] = useState<Record<string, TestLogItem[]>>({});
  const [isLoadingLogs, setIsLoadingLogs] = useState<boolean>(false);
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchTestCases().then((res) => setCases(res));
    }, 1000);

    return () => clearInterval(intervalId);
  }, []);

  useEffect(() => {
    const selectedIndex =
      selectedKeys.size > 0 ? Number(selectedKeys.values().next().value) : null;

    if (intervalId) clearInterval(intervalId);

    const fetchLogs = (selectedIndex: number) => {
      setIsLoadingLogs(true);
      fetchTestLogs(selectedIndex)
        .then((res) =>
          setLogs((prv) => ({
            ...prv,
            [selectedIndex]: res,
          }))
        )
        .finally(() => setTimeout(() => setIsLoadingLogs(false), 500));
    };

    if (selectedIndex !== null)
      intervalId = setInterval(() => fetchLogs(selectedIndex), 1000);

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [selectedKeys]);

  const handleStart = useCallback(
    (selectedIndex: number) => () => {
      triggerTest(selectedIndex)
        .then(() => console.log("Triggered"))
        .catch((err) => console.error("Failed to trigger test:", err));
    },
    []
  );

  const handleResetAll = useCallback(() => {
    resetTests()
      .then(() => console.log("Success"))
      .catch((err) => console.error("Failed to reset tests:", err));
  }, []);

  const handleDownloadCSV = useCallback(
    (selectedIndex: number) => async () => {
      const downloadUrl = `/api/download-test-report/${selectedIndex}`;
      const checkFileReady = async () => {
        const response = await fetch(downloadUrl);
        return response.ok;
      };

      const pollForFile = async () => {
        while (true) {
          const isReady = await checkFileReady();
          if (isReady) {
            const anchorElement = document.createElement("a");
            anchorElement.href = downloadUrl;
            anchorElement.click();
            break;
          }
          await new Promise((resolve) => setTimeout(resolve, 1000));
        }
      };

      await pollForFile();
    },
    []
  );

  const TestResult = useMemo(() => {
    const selectedIndex =
      selectedKeys.size > 0 ? Number(selectedKeys.values().next().value) : null;
    const hasResult =
      selectedIndex !== null
        ? ["failed", "success"].includes(cases[selectedIndex].status)
        : false;

    return selectedIndex !== null ? (
      <>
        <div className="flex items-center justify-between">
          <p className="font-bold">Test Result of #{selectedIndex + 1}</p>
          <div className="flex items-center gap-3">
            {hasResult && (
              <Button
                color="primary"
                onClick={handleDownloadCSV(selectedIndex)}
              >
                Download Result as CSV
              </Button>
            )}
            {cases[selectedIndex].status !== "in-progress" && (
              <Button color="primary" onClick={handleStart(selectedIndex)}>
                <FaPlay /> {hasResult ? "Restart" : "Start"}
              </Button>
            )}
          </div>
        </div>
        {selectedKeys.size > 0 && (
          <Card>
            <CardHeader>
              <div className="flex flex-col w-full">
                <div className="flex justify-between">
                  <p className="font-bold">Test description</p>
                  {isLoadingLogs && <Spinner size="sm" />}
                </div>
                <p className="text-sm">
                  {selectedKeys.size > 0
                    ? cases[selectedIndex].description
                    : ""}
                </p>
              </div>
            </CardHeader>
            <CardBody className={`${isExpanded ? "" : "max-h-[300px]"}`}>
              {logs[selectedIndex] && logs[selectedIndex].length > 0 ? (
                <ul className="font-mono">
                  {logs[selectedIndex].map((log, index) => (
                    <li key={index} className={`flex items-start gap-5`}>
                      <p className="text-xs text-gray-500 pt-1">
                        [{log.createdAt.toLocaleString()}]
                      </p>
                      <p
                        className={`${log.type === "error" ? "text-danger" : "opacity-50"} flex-1`}
                      >
                        {log.message}
                      </p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-center font-bold opacity-50">
                  No logs available for this test case.
                </p>
              )}
            </CardBody>
            {logs[selectedIndex] && logs[selectedIndex].length > 0 && (
              <CardFooter>
                {isExpanded ? (
                  <Button
                    className="w-full"
                    size="sm"
                    variant="bordered"
                    onClick={() => setIsExpanded(false)}
                  >
                    <FaMinus /> Show less
                  </Button>
                ) : (
                  <Button
                    className="w-full"
                    size="sm"
                    variant="bordered"
                    onClick={() => setIsExpanded(true)}
                  >
                    <FaPlus /> Show full
                  </Button>
                )}
              </CardFooter>
            )}
          </Card>
        )}
      </>
    ) : (
      <div className="flex items-center justify-center font-bold opacity-45 pt-10">
        Select Test Case to see details
      </div>
    );
  }, [selectedKeys, cases, isLoadingLogs, handleStart]);

  return (
    <DefaultLayout>
      <section className="flex flex-col justify-center gap-4 py-8 md:py-10">
        <div>
          <div className="flex items-center gap-3">
            <p className="font-bold">CarbonCopiesAI Test Assignment</p>
            <ThemeSwitch />
          </div>
          <div>
            In this test project, we automated the testing of the website
            https://video-converter.com using Playwright and OpenAI APIs. The
            objective was to ensure the reliability and performance of the file
            conversion process. We defined 3 test cases to cover various
            scenarios, allowing users to run these tests, view the results, and
            generate comprehensive reports.
          </div>
        </div>
        <div className="flex items-center justify-between">
          <p className="font-bold">Test Cases</p>
          <div className="flex items-center gap-3">
            <Button color="primary" onClick={handleResetAll}>
              <FaArrowRotateRight />
              Reset all cases
            </Button>
          </div>
        </div>
        <TestTable
          cases={cases}
          selectedKeys={selectedKeys}
          setSelectedKeys={setSelectedKeys}
        />
        {TestResult}
      </section>
    </DefaultLayout>
  );
}

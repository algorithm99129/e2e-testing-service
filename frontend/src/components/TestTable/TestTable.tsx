import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Chip,
} from "@nextui-org/react";

import { columns } from "./data";
import { useCallback } from "react";
import { TestCase, TestStatus } from "@/types";

const statusColorMap: Record<
  TestStatus,
  | "success"
  | "danger"
  | "warning"
  | "default"
  | "primary"
  | "secondary"
  | undefined
> = {
  success: "success",
  failed: "danger",
  "in-progress": "warning",
  todo: "primary",
};

interface TestTableProps {
  cases: TestCase[];
  selectedKeys: Set<string>;
  setSelectedKeys: React.Dispatch<React.SetStateAction<Set<string>>>;
}

const TestTable: React.FC<TestTableProps> = ({
  cases,
  selectedKeys,
  setSelectedKeys,
}) => {
  const renderCell = useCallback(
    (row: TestCase, columnKey: string | number) => {
      const cellValue = row[columnKey as keyof TestCase];

      switch (columnKey) {
        case "description":
          return <div>{cellValue}</div>;
        case "status":
          return (
            <Chip
              className="capitalize"
              color={statusColorMap[row.status]}
              size="sm"
              variant="flat"
            >
              {cellValue}
            </Chip>
          );
        default:
          return cellValue;
      }
    },
    []
  );

  return (
    <Table
      aria-label="Test case table"
      selectionMode="single"
      color="primary"
      selectedKeys={selectedKeys}
      onSelectionChange={(keys) => setSelectedKeys(keys as Set<string>)}
    >
      <TableHeader columns={columns}>
        {(column) => (
          <TableColumn
            key={column.uid}
            align={column.uid === "description" ? "start" : "center"}
          >
            {column.name}
          </TableColumn>
        )}
      </TableHeader>
      <TableBody emptyContent={"No test cases to display."} items={cases}>
        {(item) => (
          <TableRow key={item.id}>
            {(columnKey) => (
              <TableCell>{renderCell(item, columnKey)}</TableCell>
            )}
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
};

export default TestTable;

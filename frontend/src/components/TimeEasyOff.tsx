import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { tryPromise } from "@/lib/LangUtil";
import request from "@/service/WebClient";
import { useEffect, useState } from "react";
import { TimeEasyOffDialog } from "./TimeEasyOffDialog";
import { Type } from "class-transformer";
import { JsonUtil } from "@/lib/JsonUtil";
import { map } from "lodash";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

export class UserLeaveOvertimeData {
  additional_info: any = undefined;
  end_time: string = "";
  id: number = 0;
  leave_duration: number = 0;
  leave_or_overtime: string = "";
  leave_or_overtime_type: string = "";
  name: string = "";
  reason: string = "";
  start_time: string = "";
  user_id: number = 0;
}

export class UserLeaveOvertime {
  @Type(() => UserLeaveOvertimeData)
  data: UserLeaveOvertimeData[] = [];
  page: number = 0;
  pages: number = 0;
  per_page: number = 0;
  total: number = 0;
}

class ListRequest {
  page: number = 1;
  per_page: number = 10;
}

export const TimeEasyOff = () => {
  const [userLeaveOvertime, setUserLeaveOvertime] = useState<UserLeaveOvertime>(
    new UserLeaveOvertime()
  );

  const handleSuccess = () => {
    fetchList()
  };

  const handleClickPagination = (fields: "prev" | "next") => {
    const listRequest = new ListRequest();
    listRequest.page =
      fields === "prev"
        ? userLeaveOvertime.page - 1
        : userLeaveOvertime.page + 1;
    fetchList(listRequest);
  };

  const fetchList = async (listRequest: ListRequest = new ListRequest()) => {
    const result = await tryPromise(
      request("/api/user_leave_overtime/list", {
        method: "get",
        params: listRequest,
      })
    );
    if (result.error) {
      return console.log(result.error);
    }
    setUserLeaveOvertime(
      JsonUtil.toModelFromType(UserLeaveOvertime, result.data)
    );
  };

  useEffect(() => {
    fetchList();
  }, []);

  return (
    <div>
      <TimeEasyOffDialog onSuccess={handleSuccess} />
      <Table>
        <TableCaption>A list of your leave history.</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Leave or overtime</TableHead>
            <TableHead>Leave or overtime type</TableHead>
            <TableHead>Reason</TableHead>
            <TableHead>Start time</TableHead>
            <TableHead>End time</TableHead>
            <TableHead>Leave Duration</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {map(userLeaveOvertime.data, (item) => {
            return (
              <TableRow key={item.id}>
                <TableCell>{item.name}</TableCell>
                <TableCell>{item.leave_or_overtime}</TableCell>
                <TableCell>{item.leave_or_overtime_type}</TableCell>
                <TableCell>{item.reason}</TableCell>
                <TableCell>{item.start_time}</TableCell>
                <TableCell>{item.end_time}</TableCell>
                <TableCell>{item.leave_duration}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      <Pagination>
        <PaginationContent>
          {userLeaveOvertime.page > 1 && (
            <PaginationItem aria-disabled>
              <PaginationPrevious
                onClick={() => handleClickPagination("prev")}
              />
            </PaginationItem>
          )}
          <PaginationItem>current: {userLeaveOvertime.page}</PaginationItem>
          <PaginationItem>total: {userLeaveOvertime.total}</PaginationItem>
          {userLeaveOvertime.total >
            userLeaveOvertime.page * userLeaveOvertime.per_page && (
            <PaginationItem>
              <PaginationNext onClick={() => handleClickPagination("next")} />
            </PaginationItem>
          )}
        </PaginationContent>
      </Pagination>
    </div>
  );
};

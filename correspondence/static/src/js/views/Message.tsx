import * as React from "react";
import { parseISO, format, isToday, isYesterday } from "date-fns";
import Avatar from "../components/Avatar";
import { Message } from "../types";

function getMessageDate(date: Date): string {
  if (isToday(date)) {
    return "Today";
  }
  if (isYesterday(date)) {
    return "Yesterday";
  }

  return format(date, "iii d MMM");
}

type MessageProps = {
  message: Message;
};

export default function Message({ message }: MessageProps): React.ReactElement {
  const createdAt = parseISO(message.created_at);

  return (
    <>
      <div className="conversation__message__date">
        <time
          dateTime={format(createdAt, "yyyy-LL-dd HH:mm")}
          title={format(createdAt, "yyyy-LL-dd HH:mm")}
        >
          <strong>{getMessageDate(createdAt)}</strong>{" "}
          {format(createdAt, "HH:mm")}
        </time>
      </div>
      <div className="conversation__message">
        <div className="conversation__message__body">{message.body}</div>
        <div
          className="conversation__message__author"
          title={message.sender.name}
        >
          <Avatar name={message.sender.name} size="2rem" />
        </div>
      </div>
    </>
  );
}

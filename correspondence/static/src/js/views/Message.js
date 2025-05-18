import React from "react";
import parseISO from "date-fns/parseISO";
import format from "date-fns/format";
import isToday from "date-fns/isToday";
import isYesterday from "date-fns/isYesterday";
import Avatar from "../components/Avatar";

const getMessageDate = date => {
  if (isToday(date)) {
    return "Today";
  }
  if (isYesterday(date)) {
    return "Yesterday";
  }

  return format(date, "iii d MMM");
};

const Message = ({ message } = props) => {
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
};

export default Message;

import * as React from "react";
import Message from "./Message";
import classNames from "classnames";
import * as types from "../types";

type ThreadProps = {
  conversation: types.Conversation;
  messages: MessagePage;
  onScroll: () => void;
};

type MessagePage = {
  data: types.Message[];
  initial: boolean;
};

export default function Thread({
  conversation,
  messages,
  onScroll,
}: ThreadProps): React.ReactElement {
  const messagesEndRef = React.useRef(null);

  // keep the scroll position on scroll to the top
  React.useEffect(() => {
    if (!messages.initial) {
      return;
    }

    messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
  }, [messages]);

  const handleScroll = () => {
    if (messagesEndRef.current.scrollTop === 0) {
      onScroll();
    }
  };

  return (
    <div className="conversation__thread">
      <ul
        className="conversation__message-list"
        ref={messagesEndRef}
        onScroll={handleScroll}
      >
        {messages.data.map((message) => (
          <li
            key={message.id}
            className={classNames({
              "conversation__message-list__item": true,
              "conversation__message-list__item--received":
                conversation && message.sender.id == conversation.receiver.id,
              "conversation__message-list__item--sent":
                !conversation || message.sender.id != conversation.receiver.id,
            })}
          >
            <Message message={message} />
          </li>
        ))}
      </ul>
    </div>
  );
}

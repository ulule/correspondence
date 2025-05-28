import React, { useRef, useEffect } from "react";
import Message from "./Message";
import classNames from "classnames";

const Thread = ({ conversation, messages, onScroll } = props) => {
  const messagesEndRef = useRef(null);

  // keep the scroll position on scroll to the top
  useEffect(() => {
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
        {messages.data.map(message => (
          <li
            key={message.id}
            className={classNames({
              "conversation__message-list__item": true,
              "conversation__message-list__item--received":
                conversation && message.sender.id == conversation.receiver.id,
              "conversation__message-list__item--sent":
                !conversation || message.sender.id != conversation.receiver.id
            })}
          >
            <Message message={message} />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Thread;

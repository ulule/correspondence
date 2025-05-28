import React, { useState, useEffect } from "react";
import api from "../api";
import Thread from "./Thread";
import MessageForm from "./MessageForm";

const DEFAULT_LIMIT = 20;

const ThreadContainer = ({
  conversation,
  messageFormFocus,
  selectedUsers
} = props) => {
  const initialState = {
    data: [],
    initial: true,
    loading: false,
    finished: false,
    meta: { count: 0, next: null, total: 0 }
  };

  const [messages, setMessages] = useState(initialState);

  useEffect(() => {
    if (conversation && conversation.id) {
      if (!messages.loading) {
        setMessages({
          ...messages,
          ...{
            loading: true
          }
        });

        (async () => {
          const res = await api.get(
            `/conversations/${conversation.id}/messages/`
          );

          const data = {
            ...res.data,
            ...{
              data: res.data.data.reverse(),
              initial: true,
              loading: false
            }
          };

          setMessages(data);
        })();
      }
    } else {
      setMessages(initialState);
    }
  }, [conversation && conversation.id]);

  const onThreadScroll = async () => {
    if (messages.data.length == 0 || messages.finished) {
      return;
    }
    const last = messages.data[0];
    const res = await api.get(
      `/conversations/${conversation.id}/messages/?ending_before=${last.id}&limit=${DEFAULT_LIMIT}`
    );

    const latestResults = res.data.data.filter(
      msg1 => !messages.data.find(msg2 => msg2 === msg1)
    );

    const data = {
      ...res.data,
      ...{
        data: [...latestResults.reverse(), ...messages.data]
      },
      ...{ finished: latestResults.length < DEFAULT_LIMIT }
    };

    setMessages(data);
  };

  const onMessageSubmit = async (values, cb) => {
    let promises;

    if (conversation) {
      promises = [
        api.post(`/users/${conversation.receiver.id}/conversation/`, values)
      ];
    } else {
      promises = selectedUsers.map(user =>
        api.post(`/users/${user.id}/conversation/`, values)
      );
    }

    Promise.all(promises).then(values => {
      const newMessage = values[0].data;
      newMessage.conversation.last_message = newMessage;

      cb();

      setMessages({
        ...messages,
        ...{
          data: [...messages.data, newMessage]
        }
      });
    });
  };

  return (
    <>
      <Thread
        conversation={conversation}
        onScroll={onThreadScroll}
        messages={messages}
      />
      <MessageForm focus={messageFormFocus} onSubmit={onMessageSubmit} />
    </>
  );
};

export default ThreadContainer;

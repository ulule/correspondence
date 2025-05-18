import React, { useState, useEffect } from "react";
import api from "../api";
import MessageModel from "../models/MessageModel";
import Thread from "./Thread";
import MessageForm from "./MessageForm";

const ThreadContainer = ({
  conversation,
  messageFormFocus,
  selectedUsers
} = props) => {
  const initialState = {
    data: [],
    initial: true,
    loading: false,
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
          const res = await api.get(conversation.api.messagesUrl);

          const data = {
            ...res.data,
            ...{
              data: res.data.data.map(entry => MessageModel(entry)).reverse(),
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
    if (messages.meta.next === null) {
      return;
    }
    const last = messages.data[0];
    const res = await api.get(
      `${conversation.api.messagesUrl}?ending_before=${last.id}`
    );

    const data = {
      ...res.data,
      ...{
        data: [
          ...res.data.data.map(entry => MessageModel(entry)).reverse(),
          ...messages.data
        ]
      }
    };

    setMessages(data);
  };

  const onMessageSubmit = async (values, cb) => {
    let promises;

    if (conversation) {
      promises = [api.post(conversation.api.detailUrl, values)];
    } else {
      promises = selectedUsers.map(user =>
        api.post(`/users/${user.id}/conversation/`, values)
      );
    }

    Promise.all(promises).then(values => {
      const newMessage = MessageModel(values[0].data);
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

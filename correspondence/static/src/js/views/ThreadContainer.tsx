import * as React from "react";
import { client, getConversationMessages } from "../api";
import Thread from "./Thread";
import MessageForm from "./MessageForm";
import * as types from "../types";

const DEFAULT_LIMIT = 20;

type ThreadContainerProps = {
  conversation: types.Conversation;
  selectedUsers: types.User[];
  messageFormFocus: boolean;
};

type State = {
  data: types.Message[];
  initial: boolean;
  loading: boolean;
  finished: boolean;
  meta: types.PageMeta;
};

export default function ThreadContainer({
  conversation,
  messageFormFocus,
  selectedUsers,
}: ThreadContainerProps): React.ReactElement {
  const initialState: State = {
    data: [],
    initial: true,
    loading: false,
    finished: false,
    meta: { count: 0, next: null, total: 0 },
  };

  const [messages, setMessages] = React.useState<State>(initialState);

  React.useEffect(() => {
    if (conversation && conversation.id) {
      if (!messages.loading) {
        setMessages({
          ...messages,
          ...{
            loading: true,
          },
        });

        (async () => {
          const page = await getConversationMessages({
            conversationId: conversation.id,
          });

          setMessages({
            data: page.data.reverse(),
            initial: false,
            loading: false,
            meta: page.meta,
            finished: false,
          });
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

    const page = await getConversationMessages({
      conversationId: conversation.id,
      lastMessageId: last.id,
    });

    const latestResults = (page.data as types.Message[]).filter(
      (msg1) => !messages.data.find((msg2) => msg2 === msg1)
    );

    const data = {
      data: [...latestResults.reverse(), ...messages.data],
      meta: page.meta,
      loading: false,
      initial: false,
      finished: latestResults.length < DEFAULT_LIMIT,
    };

    setMessages(data);
  };

  const onMessageSubmit = async (values: types.P, cb: () => void) => {
    let promises;

    if (conversation) {
      promises = [
        client.post(`/users/${conversation.receiver.id}/conversation/`, values),
      ];
    } else {
      promises = selectedUsers.map((user) =>
        client.post(`/users/${user.id}/conversation/`, values)
      );
    }

    Promise.all(promises).then((values) => {
      const newMessage = values[0].data;
      newMessage.conversation.last_message = newMessage;

      cb();

      setMessages({
        ...messages,
        ...{
          data: [...messages.data, newMessage],
        },
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
}

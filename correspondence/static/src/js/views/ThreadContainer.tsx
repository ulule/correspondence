import * as React from "react";
import { createUserMessage, getConversationMessages } from "../api";
import Thread from "./Thread";
import MessageForm from "./MessageForm";
import * as types from "../types";
import { useAtomValue } from "jotai";
import { conversationAtom } from "../atoms";

const DEFAULT_LIMIT = 20;

type ThreadContainerProps = {
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

  const conversation = useAtomValue(conversationAtom);

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
            limit: DEFAULT_LIMIT,
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
      limit: DEFAULT_LIMIT,
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
        createUserMessage({ userId: conversation.receiver.id, values: values }),
      ];
    } else {
      promises = selectedUsers.map((user) =>
        createUserMessage({ userId: user.id, values: values })
      );
    }

    Promise.all(promises).then((values) => {
      const newMessage = values[0];
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

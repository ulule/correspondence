import * as React from "react";
import ConversationList from "./ConversationList";
import ConversationContainer from "./ConversationContainer";
import { getConversation, markConversation } from "../api";
import { useParams } from "react-router";
import * as types from "../types";
import { useAtom } from "jotai";
import { conversationAtom, selectedUsersAtom } from "../atoms";

const usePrevious = (value: number) => {
  const ref = React.useRef(null);
  React.useEffect(() => {
    ref.current = value;
  });
  return ref.current;
};

export default function ConversationWrapper(): React.ReactElement {
  const [isNew, setIsNew] = React.useState<boolean>(false);

  const [selectedUsers, setSelectedUsers] = useAtom(selectedUsersAtom);

  const [conversation, setConversation] = useAtom(conversationAtom);

  const onConversationAction = async (action: string) => {
    const conv = await markConversation(conversation.id, action);

    setConversation(conv);
  };

  const onNewConversation = () => {
    setSelectedUsers([]);
    setIsNew(!isNew);
  };

  const onConversationFocus = async (conversationId: number, props = {}) => {
    const conv = await getConversation(conversationId);

    setConversation(conv);
  };

  const onUserAdd = (user: types.User) => {
    const index = selectedUsers.findIndex((cur) => cur.id == user.id);

    if (index === -1) {
      const newSelectedUsers = [...selectedUsers, user];

      if (newSelectedUsers.length === 1) {
        onConversationFocus(newSelectedUsers[0].id, {
          selectedUsers: newSelectedUsers,
        });
      }
      if (newSelectedUsers.length === 0) {
        setIsNew(false);
      } else {
        setIsNew(true);
      }

      setSelectedUsers(newSelectedUsers);
    }
  };

  const onUserRemove = (user: types.User) => {
    const newSelectedUsers = selectedUsers.filter((cur) => cur.id != user.id);
    setSelectedUsers(newSelectedUsers);
    if (newSelectedUsers.length === 0) {
      setIsNew(false);
    }
  };

  const { id: conversationId } = useParams();

  const previousParamValue = usePrevious(
    conversationId && parseInt(conversationId, 10)
  );

  React.useEffect(() => {
    if (
      !previousParamValue ||
      (conversationId && previousParamValue != conversationId)
    ) {
      if (conversationId) {
        onConversationFocus(parseInt(conversationId, 10));
      }
    }
  });

  return (
    <>
      <ConversationList onNewClick={onNewConversation} isNew={isNew} />

      <ConversationContainer
        onAction={onConversationAction}
        onSearchAdd={onUserAdd}
        onSearchRemove={onUserRemove}
        isNew={isNew}
      />
    </>
  );
}

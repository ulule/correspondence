import * as React from "react";
import ConversationContainer from "./ConversationContainer";
import { getConversation, markConversation } from "../api";
import { useParams } from "react-router";
import * as types from "../types";
import { useAtom, useSetAtom } from "jotai";
import { conversationAtom, selectedUsersAtom } from "../atoms";

const usePrevious = (value: number) => {
  const ref = React.useRef(null);
  React.useEffect(() => {
    ref.current = value;
  });
  return ref.current;
};

export default function ConversationWrapper(): React.ReactElement {
  const [selectedUsers, setSelectedUsers] = useAtom(selectedUsersAtom);

  const setConversation = useSetAtom(conversationAtom);

  const onConversationFocus = async (conversationId: number, props = {}) => {
    const conv = await getConversation(conversationId);

    setConversation(conv);
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
    <ConversationContainer
    />
  );
}

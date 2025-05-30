import * as React from "react";
import ConversationList from "./ConversationList";
import ConversationContainer from "./ConversationContainer";
import { getConversation, markConversation, updateUser } from "../api";
import { useParams } from "react-router";
import * as types from "../types";
import { useAtom } from "jotai";
import { conversationAtom } from "../atoms";

const usePrevious = (value: number) => {
  const ref = React.useRef(null);
  React.useEffect(() => {
    ref.current = value;
  });
  return ref.current;
};
type State = {
  selectedUsers: types.User[];
};

export default function ConversationWrapper(): React.ReactElement {
  const initialState: State = {
    selectedUsers: [],
  };

  const [conversation, setConversation] = useAtom(conversationAtom);

  const [state, setState] = React.useState<State>(initialState);

  const { selectedUsers } = state;

  const onConversationAction = async (action: string) => {
    const conv = await markConversation(conversation.id, action);

    setConversation(conv);
  };

  const onNewConversation = () => {
    setState({
      ...state,
      ...{ selectedUsers: [] },
    });
  };

  const onConversationFocus = async (conversationId: number, props = {}) => {
    const conv = await getConversation(conversationId);

    setConversation(conv);

    setState({
      ...state,
      ...{
        userUpdateErrors: [],
      },
      ...props,
    });
  };

  const onUserAdd = (user: types.User) => {
    const index = selectedUsers.findIndex((cur) => cur.id == user.id);

    if (index === -1) {
      const newSelectedUsers = [...selectedUsers, user];

      if (newSelectedUsers.length === 1) {
        onConversationFocus(newSelectedUsers[0].id, {
          selectedUsers: newSelectedUsers,
        });
      } else {
        setState({
          selectedUsers: newSelectedUsers,
        });
      }
    }
  };

  const onUserRemove = (user: types.User) => {
    setState({
      ...state,
      ...{
        selectedUsers: selectedUsers.filter((cur) => cur.id != user.id),
      },
    });
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
    <div className="conversations__wrapper">
      <ConversationList onNewClick={onNewConversation} />

      <ConversationContainer
        onAction={onConversationAction}
        selectedUsers={selectedUsers}
        onSearchAdd={onUserAdd}
        onSearchRemove={onUserRemove}
      />
    </div>
  );
}

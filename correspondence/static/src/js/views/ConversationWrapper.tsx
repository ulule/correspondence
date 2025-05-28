import * as React from "react";
import ConversationList from "./ConversationList";
import ConversationContainer from "./ConversationContainer";
import api from "../api";
import sanitize from "../utils/sanitize";
import { useParams } from "react-router";
import * as types from "../types";

const usePrevious = (value: number) => {
  const ref = React.useRef(null);
  React.useEffect(() => {
    ref.current = value;
  });
  return ref.current;
};

const loadConversation = async (conversationId: number) => {
  let res = await api.get(`/users/${conversationId}/conversation`);
  return res.data;
};

type ConversationWrapperProps = {
  authenticatedUser: types.User;
  managers: types.User[];
  organization: types.Organization;
  countries: types.Countries;
};

type State = {
  conversation: types.Conversation | null;
  isNew: boolean;
  selectedUsers: types.User[];
  userUpdateErrors: types.Error[];
};

export default function ConversationWrapper({
  authenticatedUser,
  managers,
  organization,
  countries,
}: ConversationWrapperProps): React.ReactElement {
  const initialState: State = {
    conversation: null,
    isNew: false,
    selectedUsers: [],
    userUpdateErrors: [],
  };

  const [state, setState] = React.useState<State>(initialState);

  const { isNew, conversation, selectedUsers, userUpdateErrors } = state;

  const onUserUpdate = async ({
    values: rawValues,
  }: types.OnUserUpdateEvent) => {
    try {
      const values = sanitize(rawValues);
      const res = await api.patch(`/users/${conversation.receiver.id}/`, {
        first_name: values.first_name,
        last_name: values.last_name,
        active_campaign_id: values.active_campaign_id,
        email: values.email,
        phone_number: values.phone_number,
        manager_id: values.manager_id,
        country: values.country,
      });

      const conv = { ...conversation, ...{ receiver: res.data } };

      setState({
        ...state,
        ...{ conversation: conv },
      });
    } catch (e) {
      setState({
        ...state,
        ...{ userUpdateErrors: e.response.data?.detail },
      });
    }
  };

  const onConversationAction = async (action: string) => {
    const res = await api.post(
      `/conversations/${conversation.id}/${action}/`,
      {}
    );
    const conv = res.data;

    setState({
      ...state,
      ...{ conversation: conv },
    });
  };

  const onNewConversation = () => {
    setState({
      ...state,
      ...{ isNew: !isNew, selectedUsers: [] },
    });
  };

  const onConversationFocus = async (conversationId: number, props = {}) => {
    const conv = await loadConversation(conversationId);

    setState({
      ...state,
      ...{
        conversation: conv,
        isNew: false,
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
          isNew: true,
        });
      } else {
        setState({
          ...state,
          ...{
            conversation: null,
            isNew: true,
            userUpdateErrors: [],
            selectedUsers: newSelectedUsers,
          },
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
      <ConversationList
        onNewClick={onNewConversation}
        organization={organization}
        conversation={conversation}
        isNew={isNew}
        authenticatedUser={authenticatedUser}
      />

      <ConversationContainer
        conversation={conversation}
        isNew={isNew}
        onAction={onConversationAction}
        onUserUpdate={onUserUpdate}
        countries={countries}
        errors={userUpdateErrors}
        managers={managers}
        selectedUsers={selectedUsers}
        onSearchAdd={onUserAdd}
        onSearchRemove={onUserRemove}
      />
    </div>
  );
}

import React, { useState, useEffect, useRef } from "react";
import ConversationList from "./ConversationList";
import ConversationContainer from "./ConversationContainer";
import api from "../api";
import ConversationModel from "../models/ConversationModel";
import sanitize from "../utils/sanitize";

const usePrevious = value => {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
};

const loadConversation = async conversationId => {
  let res = await api.get(`/users/${conversationId}/conversation`);
  return ConversationModel(res.data);
};

const ConversationWrapper = ({
  match,
  authenticatedUser,
  history,
  managers,
  organization,
  countries
} = props) => {
  const initialState = {
    conversation: null,
    isNew: false,
    selectedUsers: [],
    userUpdateErrors: []
  };

  const [state, setState] = useState(initialState);

  const { isNew, conversation, selectedUsers, userUpdateErrors } = state;

  const onUserUpdate = async props => {
    try {
      const values = sanitize(props.values);
      const res = await api.patch(`/users/${conversation.receiver.id}/`, {
        first_name: values.first_name,
        last_name: values.last_name,
        active_campaign_id: values.active_campaign_id,
        email: values.email,
        phone_number: values.phone_number,
        manager_id: values.manager_id,
        country: values.country
      });

      const conv = { ...conversation, ...{ receiver: res.data } };

      setState({
        ...state,
        ...{ conversation: conv }
      });
    } catch (e) {
      setState({
        ...state,
        ...{ userUpdateErrors: e.response.data?.detail }
      });
    }
  };

  const onConversationAction = async action => {
    const res = await api.post(`/conversations/${conversation.id}/${action}/`);
    const conv = ConversationModel(res.data);

    setState({
      ...state,
      ...{ conversation: conv }
    });
  };

  const onNewConversation = () => {
    setState({
      ...state,
      ...{ isNew: !isNew, selectedUsers: [] }
    });

    history.push("/conversations");
  };

  const onConversationFocus = async (conversationId, props = {}) => {
    const conv = await loadConversation(conversationId);

    setState({
      ...state,
      ...{
        conversation: conv,
        isNew: false,
        userUpdateErrors: []
      },
      ...props
    });
  };

  const onUserAdd = user => {
    const index = selectedUsers.findIndex(cur => cur.id == user.id);

    if (index === -1) {
      const newSelectedUsers = [...selectedUsers, user];

      if (newSelectedUsers.length === 1) {
        onConversationFocus(newSelectedUsers[0].id, {
          selectedUsers: newSelectedUsers,
          isNew: true
        });
      } else {
        setState({
          ...state,
          ...{
            conversation: null,
            isNew: true,
            userUpdateErrors: [],
            selectedUsers: newSelectedUsers
          }
        });
      }
    }
  };

  const onUserRemove = user => {
    setState({
      ...state,
      ...{
        selectedUsers: selectedUsers.filter(cur => cur.id != user.id)
      }
    });
  };

  const previousParamValue = usePrevious(
    match && match.params && match.params.id
  );

  useEffect(() => {
    if (!previousParamValue || previousParamValue != match.params.id) {
      if (match.params.id) {
        onConversationFocus(match.params.id);
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
        onFocus={onConversationFocus}
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
};

export default ConversationWrapper;

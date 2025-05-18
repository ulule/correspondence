const ConversationModel = props => {
  return {
    ...props,
    ...{
      absoluteUrl: `/conversations/${props.receiver.id}`,
      api: {
        detailUrl: `/users/${props.receiver.id}/conversation/`,
        messagesUrl: `/conversations/${props.id}/messages/`
      }
    }
  };
};

export default ConversationModel;

import ConversationModel from "./ConversationModel";

const MessageModel = props => {
  return {
    ...props,
    ...{
      conversation: ConversationModel(props.conversation)
    }
  };
};

export default MessageModel;

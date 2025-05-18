import { Conversation, Message, P, Page, User } from "./types";
import requester from "./utils/requester";

const client = requester(window.CDE.api.url);

type GetConversationsQuery = {
  organizationSlug: string;
  managerId?: number;
  offset?: number;
};

type GetConversationMessagesQuery = {
  conversationId: number;
  lastMessageId?: number;
  limit: number;
};

type UpdateUserQuery = {
  userId: number;
  values: P;
};

type CreateUserQuery = {
  organizationSlug: string;
  values: P;
};

type CreateUserMessageQuery = {
  userId: number;
  values: P;
};

export async function getConversation(
  conversationId: number
): Promise<Conversation> {
  let res = await client.get(`/users/${conversationId}/conversation`);
  return res.data;
}

export async function markConversation(
  conversationId: number,
  state: string
): Promise<Conversation> {
  const res = await client.post(
    `/conversations/${conversationId}/${state}/`,
    {}
  );

  return res.data;
}

export async function getManagers(): Promise<User[]> {
  const res = await client.get(`/users/?is_staff=1`);
  return res.data.data;
}

export async function getConversationMessages({
  conversationId,
  lastMessageId,
  limit,
}: GetConversationMessagesQuery): Promise<Page<Message>> {
  let url = `/conversations/${conversationId}/messages/?limit=${limit}`;
  if (lastMessageId) {
    url = `${url}&ending_before=${lastMessageId}`;
  }
  const res = await client.get(url);
  const data = res.data;

  return data;
}

export async function updateUser({
  userId,
  values,
}: UpdateUserQuery): Promise<User> {
  const res = await client.patch(`/users/${userId}/`, values);
  return res.data;
}

export async function createUser({
  organizationSlug,
  values,
}: CreateUserQuery): Promise<User> {
  const res = await client.post(
    `/organizations/${organizationSlug}/users/`,
    values
  );
  return res.data;
}

export async function getUsers(term: string): Promise<Page<User>> {
  const res = await client.get(`/users/?q=${term}`);

  return res.data;
}

export async function createUserMessage({
  userId,
  values,
}: CreateUserMessageQuery): Promise<Message> {
  const res = await client.post(`/users/${userId}/conversation/`, values);
  return res.data;
}

export async function getConversations({
  organizationSlug,
  managerId,
  offset,
}: GetConversationsQuery): Promise<Page<Conversation>> {
  let url = `/organizations/${organizationSlug}/conversations/?limit=20`;
  if (offset) {
    url = `${url}&offset=${offset}`;
  }

  if (managerId) {
    url = `${url}&manager_id=${managerId}`;
  }

  const res = await client.get(url);
  const data = res.data;

  return data;
}

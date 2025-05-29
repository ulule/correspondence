import { atom } from "jotai";

import { Conversation, User, Message } from "./types";

export const conversationAtom = atom<Conversation>(null);

export const selectedUsers = atom<User[]>(null);

export const user = atom<User>(null);

export const messages = atom<Message[]>(null);

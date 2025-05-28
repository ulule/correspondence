export type Country = [string, string];
export type Countries = Country[];

export type User = {
  id: number;
  email: string | null;
  name: string | null;
  first_name: string | null;
  last_name: string | null;
  created_at: string;
  updated_at: string;
  phone_number: string | null;
  active_campaign_id: string;
  messages_received_count: number;
  messages_sent_count: number;
  country: string;
  manager: User | null;
};

export type Organization = {
  id: number;
  name: string;
  slug: string;
  supported_countries: string[];
  created_at: string;
  updated_at: string;
};

export type Message = {
  id: number;
  sender: User;
  created_at: string;
  updated_at: string;
  body: string;
  conversation?: Conversation | null;
};

export type Conversation = {
  id: number;
  messages_count: number;
  receiver: User;
  created_at: string;
  updated_at: string;
  unread: boolean;
  last_message: Message | null;
};

export type Values = Record<string, any>;

export type OnUserCreateEvent = {
  values: Values;
  onSuccess?: () => void;
};

export type OnUserUpdateEvent = {
  values: Values;
  onSuccess?: () => void;
};


export type PageMeta = {
  count: number;
  next: string | null;
  total: number;
  offset?: number
};

export type P = {
  [key: string]: any;
};

export type FormData = {
  [key: string]: string;
};


export type Error = {
  msg: string;
  loc: string[];
};

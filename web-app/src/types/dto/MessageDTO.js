/* src/types/dto/MessageDTO.js */

export const MessageDTO = {
  id: "",
  order_id: null,
  sender_id: null,
  receiver_id: null,
  content: "",
  is_read: false,
  created_at: new Date().toISOString(),
  updated_at: null,
  sender_name: "",
  receiver_name: ""
};

export function createMessage(overrides = {}) {
  return {
    ...MessageDTO,
    id: crypto.randomUUID(),
    ...overrides,
  };
} 
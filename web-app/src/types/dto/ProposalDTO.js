/* src/types/dto/ProposalDTO.js */

export const ProposalStatus = {
  PENDING: "pending",
  ACCEPTED: "accepted",
  REJECTED: "rejected",
  WITHDRAWN: "withdrawn"
};

export const ProposalDTO = {
  id: "",
  message: "",
  price: 0,
  estimated_duration: null,
  order_id: null,
  user_id: null,
  status: ProposalStatus.PENDING,
  created_at: new Date().toISOString(),
  updated_at: null
};

export function createProposal(overrides = {}) {
  return {
    ...ProposalDTO,
    id: crypto.randomUUID(),
    ...overrides,
  };
}

export const ProposalStatusLabels = {
  [ProposalStatus.PENDING]: "Ожидает рассмотрения",
  [ProposalStatus.ACCEPTED]: "Принято",
  [ProposalStatus.REJECTED]: "Отклонено",
  [ProposalStatus.WITHDRAWN]: "Отозвано"
};

export const ProposalStatusColors = {
  [ProposalStatus.PENDING]: "bg-yellow-100 text-yellow-800",
  [ProposalStatus.ACCEPTED]: "bg-green-100 text-green-800",
  [ProposalStatus.REJECTED]: "bg-red-100 text-red-800",
  [ProposalStatus.WITHDRAWN]: "bg-gray-100 text-gray-800"
}; 
// src/services/subscriptionService.ts
import { API_BASE_URL } from '../apiConfig';

export interface Subscription {
  availableApiID: number;
  interval: number;
  status: 'ACTIVE' | 'INACTIVE';
  subscriptionID: number;
  userID: number;
}

export const fetchSubscriptions = async (userID: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/subscriptionsByUserID/${userID}`);
    if (!response.ok) throw new Error('Failed to fetch subscriptions');
    return response.json() as Promise<Subscription[]>;
  } catch (error) {
    console.error('Failed to fetch subscriptions:', error);
    throw error;
  }
};

export const addSubscription = async (subscription: Subscription) => {
  try {
    const response = await fetch(`${API_BASE_URL}/subscriptions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(subscription),
    });
    if (!response.ok) throw new Error('Failed to add subscription');
    return response.json() as Promise<Subscription>;
  } catch (error) {
    console.error('Failed to add subscription:', error);
    throw error;
  }
};

export const removeSubscription = async (subscriptionID: number) => {
  try {
    const response = await fetch(`${API_BASE_URL}/subscriptions/${subscriptionID}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to remove subscription');
    return response.json();
  } catch (error) {
    console.error('Failed to remove subscription:', error);
    throw error;
  }
};

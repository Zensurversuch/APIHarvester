// src/services/subscriptionService.ts
import { POSTGRES_API_BASE_URL, SCHEDULER_API_BASE_URL } from '../apiConfig';

export interface Subscription {
  availableApiID: number;
  interval: number;
  status: 'ACTIVE' | 'INACTIVE';
  subscriptionID: number;
  userID: number;
}

export const fetchSubscriptions = async (userID: string) => {
  try {
    const response = await fetch(`${POSTGRES_API_BASE_URL}subscriptionsByUserID/${userID}`);
    if (!response.ok) throw new Error('Failed to fetch subscriptions');
    return response.json() as Promise<Subscription[]>;
  } catch (error) {
    console.error('Failed to fetch subscriptions:', error);
    throw error;
  }
};

export const subscribe = async (userID: string, apiID: number, interval: number): Promise<string> => {
  try {
    const response = await fetch(`${SCHEDULER_API_BASE_URL}subscribeApi/${userID}/${apiID}/${interval}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorMessage = await response.text(); 
      console.error('Failed to add subscription:', errorMessage);
      throw new Error(`Subscription failed: ${errorMessage}`); 
    }

    const result = await response.json() as Subscription;
    console.log('Subscription successful:', result);
    return 'Subscription successful!'; 
  } catch (error) {
    console.error('Failed to add subscription:', error);
    throw new Error('Subscription failed due to an error. Please try again later.'); 
  }
};


export const removeSubscription = async (subscriptionID: number) => {
  try {
    const response = await fetch(`${POSTGRES_API_BASE_URL}/subscriptions/${subscriptionID}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to remove subscription');
    return response.json();
  } catch (error) {
    console.error('Failed to remove subscription:', error);
    throw error;
  }
};

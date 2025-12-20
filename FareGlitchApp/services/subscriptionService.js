import * as RNIap from 'react-native-iap';
import { Platform, Alert } from 'react-native';

// Product IDs - MUST match what you create in App Store Connect and Google Play Console
const SUBSCRIPTION_SKUS = Platform.select({
  ios: ['com.fareglitch.app.monthly'],
  android: ['com.fareglitch.app.monthly'],
});

class SubscriptionService {
  constructor() {
    this.purchaseUpdateSubscription = null;
    this.purchaseErrorSubscription = null;
  }

  /**
   * Initialize IAP connection
   */
  async initialize() {
    try {
      const result = await RNIap.initConnection();
      console.log('IAP Connection result:', result);
      
      // Set up purchase listeners
      this.setupPurchaseListeners();
      
      return true;
    } catch (error) {
      console.error('Error initializing IAP:', error);
      return false;
    }
  }

  /**
   * Get available subscription products
   */
  async getSubscriptions() {
    try {
      const subscriptions = await RNIap.getSubscriptions({ skus: SUBSCRIPTION_SKUS });
      console.log('Available subscriptions:', subscriptions);
      return subscriptions;
    } catch (error) {
      console.error('Error getting subscriptions:', error);
      return [];
    }
  }

  /**
   * Purchase a subscription
   */
  async purchaseSubscription(sku) {
    try {
      await RNIap.requestSubscription({ sku });
    } catch (error) {
      console.error('Error purchasing subscription:', error);
      Alert.alert('Purchase Error', 'Unable to complete purchase. Please try again.');
    }
  }

  /**
   * Restore previous purchases
   */
  async restorePurchases() {
    try {
      const purchases = await RNIap.getAvailablePurchases();
      console.log('Available purchases:', purchases);
      
      if (purchases && purchases.length > 0) {
        // User has active subscription
        Alert.alert('Success', 'Your subscription has been restored!');
        return purchases;
      } else {
        Alert.alert('No Purchases', 'No previous purchases found.');
        return [];
      }
    } catch (error) {
      console.error('Error restoring purchases:', error);
      Alert.alert('Error', 'Unable to restore purchases.');
      return [];
    }
  }

  /**
   * Check if user has active subscription
   */
  async checkSubscriptionStatus() {
    try {
      const purchases = await RNIap.getAvailablePurchases();
      
      // Check if any purchase is still valid
      const hasActiveSubscription = purchases.some(purchase => {
        // iOS uses transactionReceipt, Android uses purchaseToken
        return purchase.productId === SUBSCRIPTION_SKUS[0];
      });
      
      return hasActiveSubscription;
    } catch (error) {
      console.error('Error checking subscription status:', error);
      return false;
    }
  }

  /**
   * Set up listeners for purchase updates
   */
  setupPurchaseListeners() {
    // Listen for purchase updates
    this.purchaseUpdateSubscription = RNIap.purchaseUpdatedListener(async (purchase) => {
      console.log('Purchase updated:', purchase);
      
      const receipt = purchase.transactionReceipt;
      
      if (receipt) {
        try {
          // Verify purchase with your backend server here
          // await verifyPurchaseWithBackend(receipt);
          
          // Acknowledge the purchase (Android requirement)
          if (Platform.OS === 'android') {
            await RNIap.acknowledgePurchaseAndroid({ 
              token: purchase.purchaseToken,
              developerPayload: purchase.developerPayloadAndroid 
            });
          }
          
          // Finish the transaction
          await RNIap.finishTransaction({ purchase, isConsumable: false });
          
          Alert.alert('Success!', 'Your subscription is now active! 🎉');
        } catch (error) {
          console.error('Error finishing transaction:', error);
        }
      }
    });

    // Listen for purchase errors
    this.purchaseErrorSubscription = RNIap.purchaseErrorListener((error) => {
      console.warn('Purchase error:', error);
      
      if (error.code !== 'E_USER_CANCELLED') {
        Alert.alert('Purchase Error', error.message);
      }
    });
  }

  /**
   * Clean up listeners when component unmounts
   */
  cleanup() {
    if (this.purchaseUpdateSubscription) {
      this.purchaseUpdateSubscription.remove();
      this.purchaseUpdateSubscription = null;
    }
    
    if (this.purchaseErrorSubscription) {
      this.purchaseErrorSubscription.remove();
      this.purchaseErrorSubscription = null;
    }
    
    RNIap.endConnection();
  }
}

export default new SubscriptionService();

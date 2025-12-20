import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  TouchableOpacity,
  Switch,
  Alert,
  Image,
  ActivityIndicator
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import subscriptionService from '../services/subscriptionService';

export default function ProfileScreen() {
  const [pushEnabled, setPushEnabled] = useState(true);
  const [smsEnabled, setSmsEnabled] = useState(false);
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasActiveSubscription, setHasActiveSubscription] = useState(false);

  const user = {
    name: 'Ryan Baskerville',
    email: 'ryan@example.com',
    phone: '+1 (555) 123-4567',
    subscriptionStatus: hasActiveSubscription ? 'Premium' : 'Free Trial',
    daysRemaining: hasActiveSubscription ? null : 7,
  };

  useEffect(() => {
    initializeSubscriptions();
    return () => {
      subscriptionService.cleanup();
    };
  }, []);

  const initializeSubscriptions = async () => {
    setLoading(true);
    try {
      await subscriptionService.initialize();
      const subs = await subscriptionService.getSubscriptions();
      setSubscriptions(subs);
      const isActive = await subscriptionService.checkSubscriptionStatus();
      setHasActiveSubscription(isActive);
    } catch (error) {
      console.error('Error initializing subscriptions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async () => {
    if (loading) return;

    const subscription = subscriptions[0];
    if (!subscription) {
      Alert.alert('Error', 'Subscription not available. Please try again later.');
      return;
    }

    Alert.alert(
      'Subscribe to Premium',
      `Get unlimited deal alerts for ${subscription.localizedPrice || '$4.99'}/month`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Subscribe', 
          onPress: async () => {
            setLoading(true);
            await subscriptionService.purchaseSubscription(subscription.productId);
            setLoading(false);
            // Check status again after purchase attempt
            const isActive = await subscriptionService.checkSubscriptionStatus();
            setHasActiveSubscription(isActive);
          }
        },
      ]
    );
  };

  const handleManageSubscription = async () => {
    Alert.alert(
      'Manage Subscription',
      'What would you like to do?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Restore Purchases', 
          onPress: async () => {
            setLoading(true);
            await subscriptionService.restorePurchases();
            const isActive = await subscriptionService.checkSubscriptionStatus();
            setHasActiveSubscription(isActive);
            setLoading(false);
          }
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      {/* Profile Header */}
      <LinearGradient
        colors={['#1E5BA8', '#4A9FDB']}
        style={styles.profileHeader}
      >
        <Image 
          source={require('../assets/images/logo.jpg')} 
          style={styles.avatarImage}
        />
        <Text style={styles.userName}>{user.name}</Text>
        <Text style={styles.userEmail}>{user.email}</Text>
        
        <View style={styles.subscriptionBadge}>
          <Ionicons name="star" size={16} color="#FFD700" />
          <Text style={styles.subscriptionText}>{user.subscriptionStatus}</Text>
        </View>
        {user.daysRemaining > 0 && (
          <Text style={styles.trialText}>{user.daysRemaining} days remaining</Text>
        )}
      </LinearGradient>

      {/* Subscription Card */}
      <View style={styles.section}>
        <View style={styles.premiumCard}>
          <View style={styles.premiumHeader}>
            <Ionicons name="rocket" size={30} color="#4A9FDB" />
            <Text style={styles.premiumTitle}>Upgrade to Premium</Text>
          </View>
          <Text style={styles.premiumSubtitle}>
            Get unlimited flight deal alerts and save $200+ per booking
          </Text>
          <View style={styles.premiumFeatures}>
            <View style={styles.featureRow}>
              <Ionicons name="checkmark-circle" size={18} color="#7DB84D" />
              <Text style={styles.featureText}>60-min exclusive access</Text>
            </View>
            <View style={styles.featureRow}>
              <Ionicons name="checkmark-circle" size={18} color="#7DB84D" />
              <Text style={styles.featureText}>Unlimited notifications</Text>
            </View>
            <View style={styles.featureRow}>
              <Ionicons name="checkmark-circle" size={18} color="#7DB84D" />
              <Text style={styles.featureText}>Cancel anytime</Text>
            </View>
          </View>
          <View style={styles.priceRow}>
            <Text style={styles.price}>
              {subscriptions[0]?.localizedPrice || '$4.99'}
            </Text>
            <Text style={styles.priceInterval}>/month</Text>
          </View>
          <TouchableOpacity 
            style={[styles.subscribeButton, loading && styles.subscribeButtonDisabled]} 
            onPress={handleSubscribe}
            disabled={loading || hasActiveSubscription}
          >
            {loading ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text style={styles.subscribeButtonText}>
                {hasActiveSubscription ? 'Active Subscription ✓' : 'Start Free Trial'}
              </Text>
            )}
          </TouchableOpacity>
        </View>
      </View>

      {/* Account Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account Settings</Text>
        
        <TouchableOpacity style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="person-outline" size={22} color="#1E5BA8" />
            <Text style={styles.settingText}>Edit Profile</Text>
          </View>
          <Ionicons name="chevron-forward" size={22} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="call-outline" size={22} color="#1E5BA8" />
            <Text style={styles.settingText}>Phone Number</Text>
          </View>
          <View style={styles.settingRight}>
            <Text style={styles.settingValue}>{user.phone}</Text>
            <Ionicons name="chevron-forward" size={22} color="#9CA3AF" />
          </View>
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem} onPress={handleManageSubscription}>
          <View style={styles.settingLeft}>
            <Ionicons name="card-outline" size={22} color="#1E5BA8" />
            <Text style={styles.settingText}>Manage Subscription</Text>
          </View>
          <Ionicons name="chevron-forward" size={22} color="#9CA3AF" />
        </TouchableOpacity>
      </View>

      {/* Notification Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notifications</Text>
        
        <View style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="notifications-outline" size={22} color="#1E5BA8" />
            <Text style={styles.settingText}>Push Notifications</Text>
          </View>
          <Switch
            value={pushEnabled}
            onValueChange={setPushEnabled}
            ios_backgroundColor="#E5E7EB"
            thumbColor={pushEnabled ? '#1E5BA8' : '#9CA3AF'}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="chatbubble-outline" size={22} color="#1E5BA8" />
            <Text style={styles.settingText}>SMS Alerts</Text>
          </View>
          <Switch
            value={smsEnabled}
            onValueChange={setSmsEnabled}
            ios_backgroundColor="#E5E7EB"
            thumbColor={smsEnabled ? '#1E5BA8' : '#9CA3AF'}
          />
        </View>
      </View>

      {/* Other Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>More</Text>
        
        <TouchableOpacity style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="help-circle-outline" size={22} color="#1E5BA8" />
            <Text style={styles.settingText}>Help & Support</Text>
          </View>
          <Ionicons name="chevron-forward" size={22} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="document-text-outline" size={22} color="#1E5BA8" />
            <Text style={styles.settingText}>Terms of Service</Text>
          </View>
          <Ionicons name="chevron-forward" size={22} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="shield-checkmark-outline" size={22} color="#1E5BA8" />
            <Text style={styles.settingText}>Privacy Policy</Text>
          </View>
          <Ionicons name="chevron-forward" size={22} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="logo-instagram" size={22} color="#1E5BA8" />
            <Text style={styles.settingText}>Follow on Instagram</Text>
          </View>
          <Ionicons name="chevron-forward" size={22} color="#9CA3AF" />
        </TouchableOpacity>
      </View>

      {/* Sign Out */}
      <TouchableOpacity style={styles.signOutButton}>
        <Ionicons name="log-out-outline" size={22} color="#DC2626" />
        <Text style={styles.signOutText}>Sign Out</Text>
      </TouchableOpacity>

      <View style={styles.footer}>
        <Text style={styles.footerText}>FareGlitch v1.0.0</Text>
        <Text style={styles.footerText}>© 2025 FareGlitch. All rights reserved.</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FF',
  },
  profileHeader: {
    padding: 30,
    paddingTop: 20,
    paddingBottom: 35,
    alignItems: 'center',
  },
  avatarImage: {
    width: 90,
    height: 90,
    borderRadius: 45,
    marginBottom: 15,
    borderWidth: 4,
    borderColor: '#fff',
  },
  userName: {
    fontSize: 24,
    fontWeight: '800',
    color: '#fff',
    marginBottom: 5,
  },
  userEmail: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.9,
    marginBottom: 15,
  },
  subscriptionBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.25)',
    paddingHorizontal: 15,
    paddingVertical: 6,
    borderRadius: 20,
    gap: 5,
  },
  subscriptionText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '700',
  },
  trialText: {
    color: '#fff',
    fontSize: 12,
    marginTop: 8,
    opacity: 0.9,
  },
  section: {
    paddingHorizontal: 15,
    marginTop: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#1E5BA8',
    marginBottom: 12,
    paddingHorizontal: 5,
  },
  premiumCard: {
    backgroundColor: '#fff',
    padding: 25,
    borderRadius: 20,
    borderWidth: 3,
    borderColor: '#4A9FDB',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
  },
  premiumHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 10,
  },
  premiumTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#1E5BA8',
  },
  premiumSubtitle: {
    fontSize: 14,
    color: '#626784',
    lineHeight: 20,
    marginBottom: 15,
  },
  premiumFeatures: {
    marginBottom: 15,
  },
  featureRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  featureText: {
    fontSize: 14,
    color: '#2D3142',
    fontWeight: '600',
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  price: {
    fontSize: 40,
    fontWeight: '900',
    color: '#1E5BA8',
  },
  priceInterval: {
    fontSize: 16,
    color: '#626784',
    fontWeight: '600',
    marginTop: 8,
  },
  subscribeButton: {
    backgroundColor: '#1E5BA8',
    paddingVertical: 15,
    borderRadius: 30,
    alignItems: 'center',
    elevation: 3,
    shadowColor: '#1E5BA8',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  subscribeButtonDisabled: {
    backgroundColor: '#9CA3AF',
    opacity: 0.6,
  },
  subscribeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '800',
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 10,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  settingText: {
    fontSize: 15,
    color: '#2D3142',
    fontWeight: '600',
  },
  settingRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  settingValue: {
    fontSize: 14,
    color: '#626784',
  },
  signOutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
    marginHorizontal: 15,
    marginTop: 30,
    padding: 16,
    borderRadius: 12,
    gap: 10,
    borderWidth: 2,
    borderColor: '#FEE2E2',
  },
  signOutText: {
    fontSize: 15,
    color: '#DC2626',
    fontWeight: '700',
  },
  footer: {
    alignItems: 'center',
    padding: 30,
    paddingBottom: 40,
  },
  footerText: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 5,
  },
});

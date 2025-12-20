import React from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  TouchableOpacity,
  Dimensions,
  Image
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  return (
    <ScrollView style={styles.container}>
      {/* Hero Section */}
      <LinearGradient
        colors={['#1E5BA8', '#4A9FDB', '#A8D8F0']}
        style={styles.heroSection}
      >
        <View style={styles.heroContent}>
          <Image 
            source={require('../assets/images/logo.jpg')} 
            style={styles.logo}
          />
          <Text style={styles.logoText}>
            <Text style={styles.fareText}>Fare</Text>
            <Text style={styles.glitchText}>Glitch</Text>
          </Text>
          <Text style={styles.heroTitle}>Get Flight Deals 1 Hour Before Instagram</Text>
          <Text style={styles.heroSubtitle}>
            Join 500+ smart travelers getting exclusive SMS alerts with{' '}
            <Text style={styles.highlightText}>$200+ average savings</Text> per deal
          </Text>
          <TouchableOpacity style={styles.subscribeButton}>
            <Text style={styles.subscribeButtonText}>Subscribe Now 🚀</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>

      {/* Stats Section */}
      <View style={styles.statsSection}>
        <View style={[styles.statCard, { borderColor: '#1E5BA8' }]}>
          <Text style={[styles.statNumber, { color: '#1E5BA8' }]}>$200+</Text>
          <Text style={styles.statLabel}>Avg. Savings Per Deal</Text>
        </View>
        
        <View style={[styles.statCard, { borderColor: '#4A9FDB' }]}>
          <Text style={[styles.statNumber, { color: '#4A9FDB' }]}>60 Min</Text>
          <Text style={styles.statLabel}>Exclusive Access</Text>
        </View>
        
        <View style={[styles.statCard, { borderColor: '#A8D8F0' }]}>
          <Text style={[styles.statNumber, { color: '#1E5BA8' }]}>500+</Text>
          <Text style={styles.statLabel}>Smart Travelers</Text>
        </View>
      </View>

      {/* How It Works */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>How It Works</Text>
        <Text style={styles.sectionSubtitle}>Four simple steps to never miss a deal ✨</Text>
        
        <View style={styles.stepCard}>
          <Text style={styles.stepEmoji}>🤖</Text>
          <Text style={styles.stepTitle}>1. We Scan 24/7</Text>
          <Text style={styles.stepDescription}>
            Our AI monitors millions of flights across 30+ countries, finding deals the moment they appear.
          </Text>
        </View>

        <View style={styles.stepCard}>
          <Text style={styles.stepEmoji}>📲</Text>
          <Text style={styles.stepTitle}>2. Instant Push Alert</Text>
          <Text style={styles.stepDescription}>
            Get a notification with flight details in your local currency - 1 hour before Instagram.
          </Text>
        </View>

        <View style={styles.stepCard}>
          <Text style={styles.stepEmoji}>⚡</Text>
          <Text style={styles.stepTitle}>3. Book Fast</Text>
          <Text style={styles.stepDescription}>
            You have 60 minutes of exclusive access before 50,000+ Instagram followers see it.
          </Text>
        </View>

        <View style={styles.stepCard}>
          <Text style={styles.stepEmoji}>💰</Text>
          <Text style={styles.stepTitle}>4. Save Big Money</Text>
          <Text style={styles.stepDescription}>
            Average savings of $200+ per booking. Most deals sell out in under 3 hours.
          </Text>
        </View>
      </View>

      {/* Pricing CTA */}
      <LinearGradient
        colors={['#1E5BA8', '#4A9FDB']}
        style={styles.pricingSection}
      >
        <Text style={styles.pricingTitle}>Simple Pricing. Huge Savings. 🚀</Text>
        <View style={styles.pricingCard}>
          <Text style={styles.pricingBadge}>✨ Premium Subscriber</Text>
          <View style={styles.priceContainer}>
            <Text style={styles.priceAmount}>$5</Text>
            <Text style={styles.priceInterval}>/month</Text>
          </View>
          <Text style={styles.pricingTagline}>Get every deal 1 hour before Instagram! 🔥</Text>
          
          <View style={styles.featureList}>
            <View style={styles.featureItem}>
              <Ionicons name="checkmark-circle" size={20} color="#4A9FDB" />
              <Text style={styles.featureText}>Unlimited push notifications</Text>
            </View>
            <View style={styles.featureItem}>
              <Ionicons name="checkmark-circle" size={20} color="#4A9FDB" />
              <Text style={styles.featureText}>60-minute exclusive access</Text>
            </View>
            <View style={styles.featureItem}>
              <Ionicons name="checkmark-circle" size={20} color="#4A9FDB" />
              <Text style={styles.featureText}>Currency auto-conversion</Text>
            </View>
            <View style={styles.featureItem}>
              <Ionicons name="checkmark-circle" size={20} color="#4A9FDB" />
              <Text style={styles.featureText}>Average savings: $200+</Text>
            </View>
            <View style={styles.featureItem}>
              <Ionicons name="checkmark-circle" size={20} color="#4A9FDB" />
              <Text style={styles.featureText}>Cancel anytime</Text>
            </View>
          </View>

          <TouchableOpacity style={styles.startTrialButton}>
            <Text style={styles.startTrialButtonText}>🚀 Start Free Trial</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FF',
  },
  heroSection: {
    padding: 30,
    paddingTop: 40,
    paddingBottom: 50,
    alignItems: 'center',
  },
  heroContent: {
    alignItems: 'center',
    maxWidth: 400,
  },
  logo: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    borderColor: '#fff',
    marginBottom: 15,
  },
  logoText: {
    fontSize: 32,
    fontWeight: '800',
    marginBottom: 20,
  },
  fareText: {
    color: '#fff',
  },
  glitchText: {
    color: '#FFD700',
  },
  heroTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 15,
    lineHeight: 36,
  },
  heroSubtitle: {
    fontSize: 16,
    color: '#fff',
    textAlign: 'center',
    marginBottom: 25,
    lineHeight: 24,
    opacity: 0.95,
  },
  highlightText: {
    color: '#FFD700',
    fontWeight: '700',
  },
  subscribeButton: {
    backgroundColor: '#fff',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 30,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
  },
  subscribeButtonText: {
    color: '#1E5BA8',
    fontSize: 16,
    fontWeight: '800',
  },
  statsSection: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 15,
    paddingVertical: 25,
    gap: 10,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 3,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statNumber: {
    fontSize: 32,
    fontWeight: '900',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 12,
    color: '#2D3142',
    textAlign: 'center',
    fontWeight: '600',
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 26,
    fontWeight: '800',
    color: '#1E5BA8',
    textAlign: 'center',
    marginBottom: 10,
  },
  sectionSubtitle: {
    fontSize: 16,
    color: '#626784',
    textAlign: 'center',
    marginBottom: 25,
  },
  stepCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 16,
    marginBottom: 15,
    borderWidth: 2,
    borderColor: '#E8F4FB',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
  },
  stepEmoji: {
    fontSize: 36,
    marginBottom: 10,
  },
  stepTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1E5BA8',
    marginBottom: 8,
  },
  stepDescription: {
    fontSize: 14,
    color: '#626784',
    lineHeight: 20,
  },
  pricingSection: {
    padding: 25,
    paddingTop: 35,
    paddingBottom: 40,
    marginTop: 20,
  },
  pricingTitle: {
    fontSize: 26,
    fontWeight: '800',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 25,
  },
  pricingCard: {
    backgroundColor: '#fff',
    padding: 30,
    borderRadius: 20,
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
  },
  pricingBadge: {
    fontSize: 18,
    fontWeight: '800',
    color: '#4A9FDB',
    marginBottom: 15,
  },
  priceContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  priceAmount: {
    fontSize: 56,
    fontWeight: '900',
    color: '#1E5BA8',
  },
  priceInterval: {
    fontSize: 20,
    color: '#626784',
    fontWeight: '600',
    marginTop: 10,
  },
  pricingTagline: {
    fontSize: 16,
    color: '#2D3142',
    fontWeight: '600',
    marginBottom: 25,
  },
  featureList: {
    width: '100%',
    marginBottom: 25,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    gap: 10,
  },
  featureText: {
    fontSize: 15,
    color: '#2D3142',
    fontWeight: '600',
  },
  startTrialButton: {
    backgroundColor: '#1E5BA8',
    paddingHorizontal: 40,
    paddingVertical: 16,
    borderRadius: 30,
    width: '100%',
    elevation: 5,
    shadowColor: '#1E5BA8',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 6,
  },
  startTrialButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '800',
    textAlign: 'center',
  },
});

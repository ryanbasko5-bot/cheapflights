import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { API_ENDPOINTS } from '../config/api';

export default function DealsScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch deals from API
  const fetchDeals = async () => {
    try {
      setError(null);
      const response = await fetch(API_ENDPOINTS.deals.recent);
      
      if (response.ok) {
        const data = await response.json();
        setDeals(data);
      } else {
        // Fallback to mock data if API not available
        setDeals(getMockDeals());
      }
    } catch (err) {
      console.log('API not available, using mock data:', err.message);
      // Use mock data for development
      setDeals(getMockDeals());
      setError('Using demo data - backend not connected');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDeals();
  }, []);

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    fetchDeals();
  }, []);

  // Mock data for development/testing
  const getMockDeals = () => [
    {
      id: 1,
      from: 'SYD',
      to: 'DPS',
      route: 'Sydney to Bali',
      emoji: '🏝️',
      normalPrice: '$850',
      dealPrice: '$360',
      savings: '$490',
      currency: 'USD',
      duration: '2.5 hrs',
      status: 'expired',
    },
    {
      id: 2,
      from: 'LAX',
      to: 'TYO',
      route: 'Los Angeles to Tokyo',
      emoji: '🏯',
      normalPrice: '$1,200',
      dealPrice: '$645',
      savings: '$555',
      currency: 'USD',
      duration: '1.5 hrs',
      status: 'expired',
    },
    {
      id: 3,
      from: 'LHR',
      to: 'BKK',
      route: 'London to Bangkok',
      emoji: '🌴',
      normalPrice: '£680',
      dealPrice: '£298',
      savings: '£382',
      currency: 'GBP',
      duration: '3 hrs',
      status: 'expired',
    },
    {
      id: 4,
      from: 'JFK',
      to: 'CDG',
      route: 'New York to Paris',
      emoji: '🗼',
      normalPrice: '$950',
      dealPrice: '$412',
      savings: '$538',
      currency: 'USD',
      duration: '2 hrs',
      status: 'expired',
    },
    {
      id: 5,
      from: 'SFO',
      to: 'HNL',
      route: 'San Francisco to Hawaii',
      emoji: '🌺',
      normalPrice: '$580',
      dealPrice: '$198',
      savings: '$382',
      currency: 'USD',
      duration: '4 hrs',
      status: 'expired',
    },
  ];

  return (
    <View style={styles.container}>
      {error && (
        <View style={styles.errorBanner}>
          <Ionicons name="information-circle" size={16} color="#FFA500" />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}
      
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Recent Deals</Text>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>⚡ All expired - subscribers got them first!</Text>
        </View>
      </View>

      {loading && !refreshing ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#1E5BA8" />
          <Text style={styles.loadingText}>Loading deals...</Text>
        </View>
      ) : (
        <ScrollView
          style={styles.scrollView}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        >
        {deals.map((deal) => (
          <View key={deal.id} style={styles.dealCard}>
            <View style={styles.dealHeader}>
              <View>
                <View style={styles.routeContainer}>
                  <Text style={styles.routeCode}>{deal.from}</Text>
                  <Ionicons name="arrow-forward" size={20} color="#1E5BA8" />
                  <Text style={styles.routeCode}>{deal.to}</Text>
                </View>
                <Text style={styles.routeName}>{deal.route} {deal.emoji}</Text>
              </View>
              <View style={styles.expiredBadge}>
                <Text style={styles.expiredText}>EXPIRED</Text>
              </View>
            </View>

            <View style={styles.priceSection}>
              <View style={styles.priceRow}>
                <Text style={styles.priceLabel}>Normal Price</Text>
                <Text style={styles.normalPrice}>{deal.normalPrice}</Text>
              </View>
              <View style={styles.priceRow}>
                <Text style={styles.priceLabel}>Deal Price</Text>
                <Text style={styles.dealPrice}>{deal.dealPrice}</Text>
              </View>
              <View style={[styles.priceRow, styles.savingsRow]}>
                <Ionicons name="cash-outline" size={20} color="#7DB84D" />
                <Text style={styles.savings}>Savings: {deal.savings}</Text>
              </View>
            </View>

            <View style={styles.footer}>
              <Ionicons name="time-outline" size={16} color="#626784" />
              <Text style={styles.duration}>Lasted {deal.duration}</Text>
            </View>
          </View>
        ))}

        <View style={styles.bottomCTA}>
          <Ionicons name="notifications" size={40} color="#4A9FDB" />
          <Text style={styles.ctaTitle}>Don't Miss the Next Deal!</Text>
          <Text style={styles.ctaSubtitle}>
            Subscribe now and get instant notifications for new deals before they expire.
          </Text>
          <TouchableOpacity style={styles.subscribeButton}>
            <Text style={styles.subscribeButtonText}>Subscribe for $5/month</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FF',
  },
  header: {
    padding: 20,
    paddingTop: 15,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#1E5BA8',
    marginBottom: 10,
  },
  badge: {
    backgroundColor: '#E8F4FB',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 2,
    borderColor: '#4A9FDB',
    alignSelf: 'flex-start',
  },
  badgeText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#1E5BA8',
  },
  scrollView: {
    flex: 1,
  },
  dealCard: {
    backgroundColor: '#fff',
    marginHorizontal: 15,
    marginTop: 15,
    padding: 20,
    borderRadius: 16,
    borderWidth: 3,
    borderColor: '#4A9FDB',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  dealHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  routeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 5,
  },
  routeCode: {
    fontSize: 22,
    fontWeight: '800',
    color: '#1E5BA8',
  },
  routeName: {
    fontSize: 14,
    color: '#626784',
    fontWeight: '500',
  },
  expiredBadge: {
    backgroundColor: '#1E5BA8',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  expiredText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '700',
  },
  priceSection: {
    paddingVertical: 15,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#E5E7EB',
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  priceLabel: {
    fontSize: 13,
    color: '#626784',
    fontWeight: '600',
  },
  normalPrice: {
    fontSize: 18,
    color: '#9CA3AF',
    textDecorationLine: 'line-through',
    fontWeight: '600',
  },
  dealPrice: {
    fontSize: 28,
    color: '#4A9FDB',
    fontWeight: '900',
  },
  savingsRow: {
    marginTop: 5,
    gap: 8,
  },
  savings: {
    fontSize: 16,
    color: '#7DB84D',
    fontWeight: '700',
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
    gap: 5,
  },
  duration: {
    fontSize: 13,
    color: '#626784',
    fontWeight: '500',
  },
  bottomCTA: {
    backgroundColor: '#fff',
    margin: 15,
    marginTop: 20,
    marginBottom: 30,
    padding: 30,
    borderRadius: 20,
    alignItems: 'center',
    borderWidth: 3,
    borderColor: '#A8D8F0',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  ctaTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#1E5BA8',
    marginTop: 15,
    marginBottom: 10,
    textAlign: 'center',
  },
  ctaSubtitle: {
    fontSize: 14,
    color: '#626784',
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 20,
  },
  subscribeButton: {
    backgroundColor: '#1E5BA8',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 30,
    width: '100%',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
  },
  subscribeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
    textAlign: 'center',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    color: '#626784',
  },
  errorBanner: {
    backgroundColor: '#FFF3CD',
    padding: 10,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#FFA500',
  },
  errorText: {
    fontSize: 12,
    color: '#856404',
    flex: 1,
  },
});
    shadowColor: '#1E5BA8',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
  },
  subscribeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '800',
    textAlign: 'center',
  },
});

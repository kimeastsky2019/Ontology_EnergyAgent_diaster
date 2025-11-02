import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  ProgressBar,
  Chip,
  FAB,
  Text,
} from 'react-native-paper';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';
import * as Animatable from 'react-native-animatable';

import { ApiService } from '../services/ApiService';
import { NotificationService } from '../services/NotificationService';

const screenWidth = Dimensions.get('window').width;

interface DashboardData {
  predictionAccuracy: number;
  anomalyCount: number;
  climateCorrelation: number;
  activeModels: number;
  energyConsumption: number[];
  predictions: number[];
  anomalies: any[];
  climateData: any[];
}

const DashboardScreen: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    setupRealTimeUpdates();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getDashboardData();
      setDashboardData(data);
    } catch (error) {
      Alert.alert('오류', '대시보드 데이터를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  const setupRealTimeUpdates = () => {
    // 5분마다 데이터 업데이트
    const interval = setInterval(() => {
      loadDashboardData();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handlePredictionRequest = async () => {
    try {
      await ApiService.runPrediction();
      NotificationService.showSuccess('예측이 완료되었습니다.');
      loadDashboardData();
    } catch (error) {
      Alert.alert('오류', '예측 실행에 실패했습니다.');
    }
  };

  const handleAnomalyDetection = async () => {
    try {
      await ApiService.runAnomalyDetection();
      NotificationService.showSuccess('이상치 탐지가 완료되었습니다.');
      loadDashboardData();
    } catch (error) {
      Alert.alert('오류', '이상치 탐지에 실패했습니다.');
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>데이터를 불러오는 중...</Text>
      </View>
    );
  }

  if (!dashboardData) {
    return (
      <View style={styles.errorContainer}>
        <Text>데이터를 불러올 수 없습니다.</Text>
      </View>
    );
  }

  const chartConfig = {
    backgroundColor: '#ffffff',
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    decimalPlaces: 1,
    color: (opacity = 1) => `rgba(0, 123, 255, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: '#007bff',
    },
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* KPI Cards */}
        <Animatable.View animation="fadeInDown" delay={100}>
          <View style={styles.kpiContainer}>
            <Card style={styles.kpiCard}>
              <Card.Content>
                <Title>예측 정확도</Title>
                <Paragraph style={styles.kpiValue}>
                  {dashboardData.predictionAccuracy.toFixed(1)}%
                </Paragraph>
                <ProgressBar
                  progress={dashboardData.predictionAccuracy / 100}
                  color="#4CAF50"
                  style={styles.progressBar}
                />
              </Card.Content>
            </Card>

            <Card style={styles.kpiCard}>
              <Card.Content>
                <Title>이상치 탐지</Title>
                <Paragraph style={styles.kpiValue}>
                  {dashboardData.anomalyCount}개
                </Paragraph>
                <Chip
                  mode="outlined"
                  textStyle={{ color: dashboardData.anomalyCount > 5 ? '#f44336' : '#4CAF50' }}
                >
                  {dashboardData.anomalyCount > 5 ? '주의' : '정상'}
                </Chip>
              </Card.Content>
            </Card>
          </View>
        </Animatable.View>

        <Animatable.View animation="fadeInUp" delay={200}>
          <View style={styles.kpiContainer}>
            <Card style={styles.kpiCard}>
              <Card.Content>
                <Title>기후 상관관계</Title>
                <Paragraph style={styles.kpiValue}>
                  {dashboardData.climateCorrelation.toFixed(2)}
                </Paragraph>
                <Chip mode="outlined">
                  {dashboardData.climateCorrelation > 0.7 ? '강한 상관관계' : '보통 상관관계'}
                </Chip>
              </Card.Content>
            </Card>

            <Card style={styles.kpiCard}>
              <Card.Content>
                <Title>활성 모델</Title>
                <Paragraph style={styles.kpiValue}>
                  {dashboardData.activeModels}개
                </Paragraph>
                <Chip mode="outlined" textStyle={{ color: '#2196F3' }}>
                  앙상블 모델
                </Chip>
              </Card.Content>
            </Card>
          </View>
        </Animatable.View>

        {/* Charts */}
        <Animatable.View animation="fadeInLeft" delay={300}>
          <Card style={styles.chartCard}>
            <Card.Content>
              <Title>에너지 소비 패턴</Title>
              <LineChart
                data={{
                  labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                  datasets: [
                    {
                      data: dashboardData.energyConsumption,
                      color: (opacity = 1) => `rgba(0, 123, 255, ${opacity})`,
                      strokeWidth: 2,
                    },
                  ],
                }}
                width={screenWidth - 40}
                height={220}
                chartConfig={chartConfig}
                bezier
                style={styles.chart}
              />
            </Card.Content>
          </Card>
        </Animatable.View>

        <Animatable.View animation="fadeInRight" delay={400}>
          <Card style={styles.chartCard}>
            <Card.Content>
              <Title>예측 결과</Title>
              <BarChart
                data={{
                  labels: ['1시간', '2시간', '3시간', '4시간', '5시간'],
                  datasets: [
                    {
                      data: dashboardData.predictions,
                    },
                  ],
                }}
                width={screenWidth - 40}
                height={220}
                chartConfig={chartConfig}
                style={styles.chart}
              />
            </Card.Content>
          </Card>
        </Animatable.View>
      </ScrollView>

      {/* Floating Action Buttons */}
      <View style={styles.fabContainer}>
        <FAB
          style={styles.fab}
          icon="trending-up"
          label="예측 실행"
          onPress={handlePredictionRequest}
        />
        <FAB
          style={[styles.fab, styles.fabSecondary]}
          icon="warning"
          label="이상치 탐지"
          onPress={handleAnomalyDetection}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  kpiContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  kpiCard: {
    flex: 1,
    marginHorizontal: 4,
  },
  kpiValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007bff',
  },
  progressBar: {
    marginTop: 8,
  },
  chartCard: {
    marginBottom: 16,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  fabContainer: {
    position: 'absolute',
    bottom: 16,
    right: 16,
    flexDirection: 'column',
  },
  fab: {
    marginBottom: 8,
  },
  fabSecondary: {
    backgroundColor: '#ff9800',
  },
});

export default DashboardScreen;

"""
🧪 TESTES DE PERFORMANCE - SISTEMA DE SUREBETS
==============================================
Testes para medir e validar performance do sistema.
"""

import pytest
import time
import threading
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch
import logging

from database.database import get_db


class TestDatabasePerformance:
    """Testes de performance do banco de dados."""
    
    @pytest.mark.performance
    def test_bulk_insert_performance(self, clean_database, benchmark_timer, memory_profiler):
        """Testa performance de inserção em massa."""
        db = clean_database
        memory_profiler.start()
        
        # Preparar dados em lote
        batch_sizes = [100, 500, 1000, 5000]
        results = {}
        
        for batch_size in batch_sizes:
            data = [
                (f'Bookmaker {i}', f'https://api{i}.com', True, 100, 15)
                for i in range(batch_size)
            ]
            
            benchmark_timer.start()
            db.execute_many(
                "INSERT INTO bookmakers (name, api_url, is_active, rate_limit, timeout_seconds) VALUES (?, ?, ?, ?, ?)",
                data
            )
            benchmark_timer.stop()
            
            elapsed_ms = benchmark_timer.elapsed_ms()
            throughput = batch_size / (elapsed_ms / 1000)  # registros por segundo
            
            results[batch_size] = {
                'elapsed_ms': elapsed_ms,
                'throughput': throughput
            }
            
            # Limpar dados para próximo teste
            db.execute("DELETE FROM bookmakers")
        
        # Validar performance
        for batch_size, metrics in results.items():
            assert metrics['throughput'] > 100  # Mínimo 100 registros/segundo
            logging.info(f"Batch {batch_size}: {metrics['elapsed_ms']:.2f}ms, {metrics['throughput']:.2f} records/sec")
        
        memory_usage_mb = memory_profiler.get_memory_usage_mb()
        assert memory_usage_mb < 100  # Não deve usar mais que 100MB
    
    @pytest.mark.performance
    def test_complex_query_performance(self, populated_database, benchmark_timer):
        """Testa performance de queries complexas."""
        db = populated_database
        
        # Query complexa com múltiplos JOINs
        complex_query = """
        SELECT 
            e.home_team,
            e.away_team,
            e.start_time,
            s.name as sport_name,
            l.name as league_name,
            m.name as market_name,
            sel.name as selection_name,
            sel.odds,
            b.name as bookmaker_name,
            COUNT(ao.id) as arbitrage_count,
            AVG(ao.profit_percentage) as avg_profit
        FROM events e
        JOIN leagues l ON e.league_id = l.id
        JOIN sports s ON l.sport_id = s.id
        JOIN selections sel ON e.id = sel.event_id
        JOIN markets m ON sel.market_id = m.id
        JOIN bookmakers b ON sel.bookmaker_id = b.id
        LEFT JOIN arbitrage_opportunities ao ON e.id = ao.event_id
        WHERE e.is_active = 1
        GROUP BY e.id, sel.id
        ORDER BY e.start_time, avg_profit DESC
        """
        
        # Executar múltiplas vezes para medir consistência
        execution_times = []
        
        for _ in range(10):
            benchmark_timer.start()
            results = db.fetch(complex_query)
            benchmark_timer.stop()
            
            execution_times.append(benchmark_timer.elapsed_ms())
          # Análise de performance
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        min_time = min(execution_times)
        
        assert avg_time < 100  # Tempo médio < 100ms
        assert max_time < 200  # Tempo máximo < 200ms
        assert len(results) > 0
        
        logging.info(f"Complex query: avg={avg_time:.2f}ms, min={min_time:.2f}ms, max={max_time:.2f}ms")
    
    @pytest.mark.performance
    def test_concurrent_read_performance(self, threading_database):
        """Testa performance de leituras concorrentes."""
        db = threading_database
        
        def read_worker(worker_id):
            """Worker para leitura concorrente."""
            start_time = time.perf_counter()
            
            # Simular diferentes tipos de consulta
            queries = [
                "SELECT * FROM events WHERE is_active = 1",
                "SELECT * FROM selections WHERE odds > 2.0",
                "SELECT * FROM arbitrage_opportunities WHERE profit_percentage > 3.0",
                "SELECT * FROM v_active_opportunities LIMIT 10"
            ]
            
            results = []
            for query in queries:
                query_start = time.perf_counter()
                data = db.fetch(query)
                query_end = time.perf_counter()
                
                results.append({
                    'query': query,
                    'rows': len(data),
                    'time_ms': (query_end - query_start) * 1000
                })
            
            end_time = time.perf_counter()
            total_time = (end_time - start_time) * 1000
            
            return {
                'worker_id': worker_id,
                'total_time_ms': total_time,
                'queries': results
            }
        
        # Executar com múltiplas threads
        num_workers = 10
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(read_worker, i) for i in range(num_workers)]
            
            worker_results = []
            for future in as_completed(futures):
                worker_results.append(future.result())        
        # Analisar resultados
        total_times = [r['total_time_ms'] for r in worker_results]
        avg_total_time = sum(total_times) / len(total_times)
        max_total_time = max(total_times)
        
        assert avg_total_time < 1000  # Tempo médio < 1 segundo
        assert max_total_time < 2000  # Tempo máximo < 2 segundos
        
        logging.info(f"Concurrent reads: {num_workers} workers, avg={avg_total_time:.2f}ms, max={max_total_time:.2f}ms")
    
    @pytest.mark.performance
    def test_mixed_workload_performance(self, threading_database):
        """Testa performance com workload misto (read/write)."""
        db = threading_database
        
        def read_worker():
            """Worker de leitura."""
            start_time = time.perf_counter()
            for _ in range(50):
                db.fetch("SELECT * FROM v_active_opportunities LIMIT 5")
            end_time = time.perf_counter()
            return (end_time - start_time) * 1000
        
        def write_worker():
            """Worker de escrita."""
            start_time = time.perf_counter()
            for i in range(10):
                # Simular atualização de odds
                selection_id = random.randint(2001, 2030)
                new_odds = round(random.uniform(1.5, 5.0), 2)
                
                db.execute(
                    "UPDATE selections SET odds = ? WHERE id = ?",
                    (new_odds, selection_id)
                )
            end_time = time.perf_counter()
            return (end_time - start_time) * 1000
        
        # Executar workload misto
        with ThreadPoolExecutor(max_workers=8) as executor:
            # 5 workers de leitura, 3 de escrita
            read_futures = [executor.submit(read_worker) for _ in range(5)]
            write_futures = [executor.submit(write_worker) for _ in range(3)]
            
            read_times = [f.result() for f in read_futures]
            write_times = [f.result() for f in write_futures]
        
        avg_read_time = sum(read_times) / len(read_times)
        avg_write_time = sum(write_times) / len(write_times)
        
        assert avg_read_time < 1000  # Leituras < 1 segundo
        assert avg_write_time < 500   # Escritas < 500ms
        
        logging.info(f"Mixed workload: reads={avg_read_time:.2f}ms, writes={avg_write_time:.2f}ms")


class TestArbitragePerformance:
    """Testes de performance específicos para arbitragem."""
    
    @pytest.mark.performance
    def test_arbitrage_detection_speed(self, populated_database, benchmark_timer):
        """Testa velocidade de detecção de arbitragem."""
        db = populated_database
        
        # Simular detecção de arbitragem
        detection_query = """
        WITH odds_matrix AS (
            SELECT 
                s.event_id,
                s.market_id,
                s.name as selection_name,
                s.odds,
                b.name as bookmaker_name,
                ROW_NUMBER() OVER (PARTITION BY s.event_id, s.market_id, s.name ORDER BY s.odds DESC) as rank
            FROM selections s
            JOIN bookmakers b ON s.bookmaker_id = b.id
            WHERE s.is_active = 1
        ),
        best_odds AS (
            SELECT event_id, market_id, selection_name, odds, bookmaker_name
            FROM odds_matrix 
            WHERE rank = 1
        ),
        arbitrage_calc AS (
            SELECT 
                event_id,
                market_id,
                SUM(1.0/odds) as total_implied_prob,
                COUNT(*) as selection_count
            FROM best_odds
            GROUP BY event_id, market_id
            HAVING COUNT(*) >= 2
        )
        SELECT 
            ac.*,
            (1.0 - ac.total_implied_prob) * 100 as profit_percentage
        FROM arbitrage_calc ac
        WHERE ac.total_implied_prob < 1.0
        ORDER BY profit_percentage DESC
        """
        
        # Medir tempo de detecção
        detection_times = []
        
        for _ in range(20):
            benchmark_timer.start()
            opportunities = db.fetch(detection_query)
            benchmark_timer.stop()
            
            detection_times.append(benchmark_timer.elapsed_ms())
        
        avg_detection_time = sum(detection_times) / len(detection_times)
        max_detection_time = max(detection_times)
        
        assert avg_detection_time < 50   # Detecção média < 50ms
        assert max_detection_time < 100  # Detecção máxima < 100ms
        
        logging.info(f"Arbitrage detection: avg={avg_detection_time:.2f}ms, max={max_detection_time:.2f}ms")
    
    @pytest.mark.performance
    def test_stake_calculation_performance(self, populated_database, benchmark_timer):
        """Testa performance do cálculo de stakes."""
        db = populated_database
        
        # Buscar oportunidades para calcular stakes
        opportunities = db.fetch("""
            SELECT * FROM arbitrage_opportunities 
            WHERE profit_percentage > 2.0
            LIMIT 10
        """)
        
        def calculate_stakes(opportunity, total_stake=1000):
            """Simular cálculo de stakes."""
            import json
            
            selections = json.loads(opportunity['selections_json'])['selections']
            
            # Cálculo de Kelly Criterion simplificado
            total_inv_odds = sum(1/sel['odds'] for sel in selections)
            stakes = []
            
            for sel in selections:
                stake_percentage = (1/sel['odds']) / total_inv_odds
                stake_amount = total_stake * stake_percentage
                
                stakes.append({
                    'bookmaker': sel['bookmaker'],
                    'selection': sel['selection'],
                    'amount': round(stake_amount, 2),
                    'percentage': round(stake_percentage * 100, 2)
                })
            
            return stakes
        
        # Medir tempo de cálculo
        calculation_times = []
        
        for opportunity in opportunities:
            benchmark_timer.start()
            stakes = calculate_stakes(opportunity)
            benchmark_timer.stop()
            
            calculation_times.append(benchmark_timer.elapsed_ms())
            assert len(stakes) > 0
        
        if calculation_times:
            avg_calc_time = sum(calculation_times) / len(calculation_times)
            assert avg_calc_time < 1  # Cálculo < 1ms por oportunidade
            
            logging.info(f"Stake calculation: avg={avg_calc_time:.3f}ms per opportunity")


class TestScalabilityTests:
    """Testes de escalabilidade."""
    
    @pytest.mark.performance
    def test_large_dataset_performance(self, clean_database, benchmark_timer):
        """Testa performance com dataset grande."""
        db = clean_database
        
        # Inserir dados em massa
        logging.info("Inserindo dados em massa...")
        
        # Bookmakers
        bookmaker_data = [(f'Bookmaker {i}', f'https://api{i}.com', True) for i in range(100)]
        db.execute_many(
            "INSERT INTO bookmakers (name, api_url, is_active) VALUES (?, ?, ?)",
            bookmaker_data
        )
        
        # Sports e Leagues
        sport_id = db.insert('sports', {'name': 'Test Sport', 'slug': 'test-sport', 'is_active': True})
        
        league_data = [(sport_id, f'League {i}', f'league-{i}', 'Test Country', True) for i in range(50)]
        db.execute_many(
            "INSERT INTO leagues (sport_id, name, slug, country, is_active) VALUES (?, ?, ?, ?, ?)",
            league_data
        )
        
        # Markets
        market_id = db.insert('markets', {'name': 'Test Market', 'slug': 'test-market', 'is_active': True})
        
        # Events (10,000 eventos)
        logging.info("Inserindo 10,000 eventos...")
        event_data = [
            (f'EXT_{i}', random.randint(1, 50), f'Home {i}', f'Away {i}', 
             '2025-06-01 15:00:00', 'upcoming', True)
            for i in range(10000)
        ]
        
        benchmark_timer.start()
        db.execute_many(
            "INSERT INTO events (external_id, league_id, home_team, away_team, start_time, status, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
            event_data
        )
        benchmark_timer.stop()
        
        insert_time = benchmark_timer.elapsed_ms()
        logging.info(f"Inserted 10,000 events in {insert_time:.2f}ms")
        
        # Testar queries em dataset grande
        benchmark_timer.start()
        events = db.fetch("SELECT COUNT(*) as count FROM events WHERE is_active = 1")
        benchmark_timer.stop()
        
        count_time = benchmark_timer.elapsed_ms()
        assert events[0]['count'] == 10000
        assert count_time < 100  # Count deve ser rápido
        
        # Testar query com JOIN
        benchmark_timer.start()
        joined_data = db.fetch("""
            SELECT e.home_team, e.away_team, l.name as league_name
            FROM events e
            JOIN leagues l ON e.league_id = l.id
            LIMIT 1000        """)
        benchmark_timer.stop()
        
        join_time = benchmark_timer.elapsed_ms()
        assert len(joined_data) == 1000
        assert join_time < 200  # JOIN deve ser razoavelmente rápido
        
        logging.info(f"Large dataset: count={count_time:.2f}ms, join={join_time:.2f}ms")
    
    @pytest.mark.performance
    def test_concurrent_stress_test(self, threading_database):
        """Teste de stress com alta concorrência."""
        db = threading_database
        
        def stress_worker(worker_id, operations=100):
            """Worker para teste de stress."""
            errors = 0
            success = 0
            
            for i in range(operations):
                try:
                    operation_type = random.choice(['read', 'write', 'read', 'read'])  # Mais leituras
                    
                    if operation_type == 'read':
                        # Operação de leitura
                        query = random.choice([
                            "SELECT * FROM events WHERE is_active = 1 LIMIT 10",
                            "SELECT * FROM selections WHERE odds > 2.0 LIMIT 10",
                            "SELECT * FROM v_active_opportunities LIMIT 5"
                        ])
                        db.fetch(query)
                    
                    else:
                        # Operação de escrita (atualização de odds)
                        selection_id = random.randint(2001, 2030)
                        new_odds = round(random.uniform(1.5, 5.0), 2)
                        db.execute(
                            "UPDATE selections SET odds = ? WHERE id = ?",
                            (new_odds, selection_id)
                        )
                    
                    success += 1
                    
                except Exception as e:
                    errors += 1
                    logging.info(f"Worker {worker_id} error: {e}")
            
            return {'worker_id': worker_id, 'success': success, 'errors': errors}
        
        # Executar teste de stress
        num_workers = 20
        operations_per_worker = 50
        
        start_time = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(stress_worker, i, operations_per_worker) 
                for i in range(num_workers)
            ]
            
            results = [f.result() for f in as_completed(futures)]
        
        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000
        
        # Analisar resultados
        total_operations = sum(r['success'] + r['errors'] for r in results)
        total_errors = sum(r['errors'] for r in results)
        error_rate = (total_errors / total_operations) * 100 if total_operations > 0 else 0
        
        throughput = total_operations / (total_time / 1000)  # ops/second
        
        assert error_rate < 5  # Taxa de erro < 5%
        assert throughput > 100  # Throughput > 100 ops/sec
        
        logging.info(f"Stress test: {num_workers} workers, {total_operations} ops, {error_rate:.2f}% errors, {throughput:.2f} ops/sec")

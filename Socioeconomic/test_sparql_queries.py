#!/usr/bin/env python3
"""
Test SPARQL queries against the NC Exposome Knowledge Graph
"""

from rdflib import Graph
import sys


def load_graph(filename='nc_exposome_kg_ontology.ttl'):
    """Load the knowledge graph"""
    print(f"Loading knowledge graph from {filename}...")
    g = Graph()
    g.parse(filename, format='turtle')
    print(f"✓ Loaded {len(g)} triples")
    return g


def test_query_1_1(g):
    """Test Query 1.1: List All Counties"""
    print("\n" + "="*80)
    print("Test Query 1.1: List All Counties")
    print("="*80)

    query = """
    PREFIX ex: <http://example.org/nc-exposome/>
    PREFIX schema: <http://schema.org/>

    SELECT ?county ?name ?fips ?population
    WHERE {
      ?county a ex:County ;
              schema:name ?name ;
              schema:identifier ?fips .
      OPTIONAL { ?county schema:population ?population }
    }
    ORDER BY ?name
    LIMIT 10
    """

    results = g.query(query)
    print(f"\nFound {len(results)} counties (showing first 10):\n")
    print(f"{'County Name':<20} {'FIPS':<8} {'Population':>12}")
    print("-" * 45)

    for row in results:
        pop = f"{int(row.population):,}" if row.population else "N/A"
        print(f"{str(row.name):<20} {str(row.fips):<8} {pop:>12}")

    return len(results) > 0


def test_query_1_2(g):
    """Test Query 1.2: List All Indicators"""
    print("\n" + "="*80)
    print("Test Query 1.2: List All Indicators with Ontology Mappings")
    print("="*80)

    query = """
    PREFIX ex: <http://example.org/nc-exposome/>
    PREFIX exo: <http://purl.obolibrary.org/obo/ExO_>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?indicator ?label
    WHERE {
      ?indicator a exo:0000000 ;
                 rdfs:label ?label .
    }
    ORDER BY ?label
    """

    results = g.query(query)
    print(f"\nFound {len(results)} indicators:\n")

    for row in results:
        print(f"  - {row.label}")

    return len(results) > 0


def test_query_2_1(g):
    """Test Query 2.1: PM2.5 and Diabetes Correlation"""
    print("\n" + "="*80)
    print("Test Query 2.1: Counties with High PM2.5 and Diabetes")
    print("="*80)

    query = """
    PREFIX ex: <http://example.org/nc-exposome/>
    PREFIX schema: <http://schema.org/>
    PREFIX qb: <http://purl.org/linked-data/cube#>

    SELECT ?countyName ?pm25 ?diabetes
    WHERE {
      ?county a ex:County ;
              schema:name ?countyName .

      ?obs1 a qb:Observation ;
            schema:location ?county ;
            ex:measuredIndicator <http://example.org/nc-exposome/indicator/pm25> ;
            schema:value ?pm25 .

      ?obs2 a qb:Observation ;
            schema:location ?county ;
            ex:measuredIndicator <http://example.org/nc-exposome/indicator/diabetes_pct> ;
            schema:prevalence ?diabetes .

      FILTER(?pm25 > 8.0)
      FILTER(?diabetes > 11.0)
    }
    ORDER BY DESC(?pm25)
    """

    results = g.query(query)
    print(f"\nFound {len(results)} counties with PM2.5 > 8.0 and Diabetes > 11.0%:\n")
    print(f"{'County':<20} {'PM2.5':>8} {'Diabetes %':>12}")
    print("-" * 45)

    for row in results:
        print(f"{str(row.countyName):<20} {float(row.pm25):>8.1f} {float(row.diabetes):>12.1f}")

    return True  # Query may return 0 results legitimately


def test_query_3_1(g):
    """Test Query 3.1: Poverty and Health Outcomes"""
    print("\n" + "="*80)
    print("Test Query 3.1: High-Poverty Counties and Health Outcomes")
    print("="*80)

    query = """
    PREFIX ex: <http://example.org/nc-exposome/>
    PREFIX schema: <http://schema.org/>
    PREFIX qb: <http://purl.org/linked-data/cube#>

    SELECT ?countyName ?poverty ?obesity ?diabetes
    WHERE {
      ?county a ex:County ;
              schema:name ?countyName .

      ?pov a qb:Observation ;
           schema:location ?county ;
           ex:measuredIndicator <http://example.org/nc-exposome/indicator/poverty_rate> ;
           schema:value ?poverty .

      ?ob a qb:Observation ;
          schema:location ?county ;
          ex:measuredIndicator <http://example.org/nc-exposome/indicator/obesity_pct> ;
          schema:prevalence ?obesity .

      ?dia a qb:Observation ;
           schema:location ?county ;
           ex:measuredIndicator <http://example.org/nc-exposome/indicator/diabetes_pct> ;
           schema:prevalence ?diabetes .

      FILTER(?poverty > 15.0)
    }
    ORDER BY DESC(?poverty)
    LIMIT 10
    """

    results = g.query(query)
    print(f"\nFound {len(results)} high-poverty counties (>15%):\n")
    print(f"{'County':<20} {'Poverty %':>10} {'Obesity %':>10} {'Diabetes %':>12}")
    print("-" * 60)

    for row in results:
        print(f"{str(row.countyName):<20} {float(row.poverty):>10.1f} "
              f"{float(row.obesity):>10.1f} {float(row.diabetes):>12.1f}")

    return len(results) > 0


def test_query_5_1(g):
    """Test Query 5.1: Strong Correlations"""
    print("\n" + "="*80)
    print("Test Query 5.1: Strong Statistical Correlations (|r| > 0.8)")
    print("="*80)

    query = """
    PREFIX ex: <http://example.org/nc-exposome/>
    PREFIX schema: <http://schema.org/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?indicator1Label ?indicator2Label ?correlation
    WHERE {
      ?corr a ex:StatisticalAssociation ;
            schema:about ?indicator1 , ?indicator2 ;
            schema:value ?correlation .

      ?indicator1 rdfs:label ?indicator1Label .
      ?indicator2 rdfs:label ?indicator2Label .

      FILTER(?indicator1 != ?indicator2)
      FILTER(ABS(?correlation) > 0.8)
    }
    ORDER BY DESC(?correlation)
    LIMIT 15
    """

    results = g.query(query)
    print(f"\nFound {len(results)} strong correlations:\n")
    print(f"{'Indicator 1':<30} {'Indicator 2':<30} {'Correlation':>12}")
    print("-" * 80)

    for row in results:
        ind1 = str(row.indicator1Label)[:28]
        ind2 = str(row.indicator2Label)[:28]
        corr = float(row.correlation)
        print(f"{ind1:<30} {ind2:<30} {corr:>12.3f}")

    return len(results) > 0


def test_query_4_1(g):
    """Test Query 4.1: Top 5 Populous Counties"""
    print("\n" + "="*80)
    print("Test Query 4.1: Compare Top 5 Populous Counties")
    print("="*80)

    query = """
    PREFIX ex: <http://example.org/nc-exposome/>
    PREFIX schema: <http://schema.org/>
    PREFIX qb: <http://purl.org/linked-data/cube#>

    SELECT ?countyName ?population ?medianIncome ?poverty
    WHERE {
      ?county a ex:County ;
              schema:name ?countyName ;
              schema:population ?population .

      ?inc a qb:Observation ;
           schema:location ?county ;
           ex:measuredIndicator <http://example.org/nc-exposome/indicator/median_income> ;
           schema:value ?medianIncome .

      ?pov a qb:Observation ;
           schema:location ?county ;
           ex:measuredIndicator <http://example.org/nc-exposome/indicator/poverty_rate> ;
           schema:value ?poverty .
    }
    ORDER BY DESC(?population)
    LIMIT 5
    """

    results = g.query(query)
    print(f"\nTop 5 populous counties:\n")
    print(f"{'County':<20} {'Population':>12} {'Med Income':>12} {'Poverty %':>10}")
    print("-" * 60)

    for row in results:
        pop = f"{int(row.population):,}"
        income = f"${int(row.medianIncome):,}"
        pov = float(row.poverty)
        print(f"{str(row.countyName):<20} {pop:>12} {income:>12} {pov:>10.1f}")

    return len(results) > 0


def main():
    """Run all tests"""
    print("="*80)
    print("SPARQL Query Test Suite for NC Exposome Knowledge Graph")
    print("="*80)

    try:
        # Load graph
        g = load_graph('nc_exposome_kg_ontology.ttl')

        # Run tests
        tests = [
            ("List All Counties", test_query_1_1),
            ("List All Indicators", test_query_1_2),
            ("PM2.5 and Diabetes", test_query_2_1),
            ("Poverty and Health", test_query_3_1),
            ("Strong Correlations", test_query_5_1),
            ("Top 5 Counties", test_query_4_1),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                success = test_func(g)
                results.append((test_name, "✓ PASS" if success else "✗ FAIL"))
            except Exception as e:
                print(f"\n✗ ERROR in {test_name}: {e}")
                results.append((test_name, "✗ ERROR"))

        # Summary
        print("\n" + "="*80)
        print("Test Summary")
        print("="*80)
        for test_name, result in results:
            print(f"{test_name:<40} {result}")

        passed = sum(1 for _, r in results if "PASS" in r)
        total = len(results)
        print(f"\n{passed}/{total} tests passed")

        if passed == total:
            print("\n✓ All tests passed!")
            return 0
        else:
            print(f"\n✗ {total - passed} test(s) failed")
            return 1

    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

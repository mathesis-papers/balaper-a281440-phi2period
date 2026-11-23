import argparse
from functools import cache
from fractions import Fraction
import hashlib
import json
from math import comb, gcd, lcm, prod
from pathlib import Path


def multiply(left, right, modulus=None, length=None):
    size = len(left) + len(right) - 1
    if length is not None:
        size = min(size, length)
    result = [0] * size
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            position = left_index + right_index
            if position >= size:
                break
            result[position] += left_value * right_value
    if modulus is not None:
        result = [value % modulus for value in result]
    return result


def derivative(polynomial):
    return [index * value for index, value in enumerate(polynomial) if index]


def add(left, right, left_scale=1, right_scale=1):
    size = max(len(left), len(right))
    return [left_scale * (left[index] if index < len(left) else 0)
            + right_scale * (right[index] if index < len(right) else 0)
            for index in range(size)]


def step(polynomial, exponent, parity, modulus=None, length=None):
    first = add(polynomial, multiply([1, 1], derivative(polynomial)), parity, 2)
    second = add(multiply([1, parity + exponent - 1], first),
                 multiply([0, 1, 1], derivative(first)), 1, 2)
    return multiply([comb(exponent - 2, index) for index in range(exponent - 1)],
                    second, modulus, length)


def column(exponent, power, count, modulus=None):
    parity = power % 2
    polynomial = [comb(power // 2, index) for index in range(power // 2 + 1)]
    length = (modulus + 1) // 2 if modulus else None
    if length:
        polynomial = polynomial[:length]
    values = []
    for index in range(count):
        values.append(polynomial[0] % modulus if modulus else polynomial[0])
        if index + 1 < count:
            polynomial = step(polynomial, exponent, parity, modulus, length)
    return values


@cache
def recurrence(exponent, power, index):
    if index == 0:
        return 1
    return power * (
        (power + exponent - 1) * recurrence(exponent, power + 2 * exponent - 2, index - 1)
        - (power + exponent - 2) * recurrence(exponent, power + 2 * exponent - 4, index - 1))


def factorization(number):
    result = []
    divisor = 2
    while divisor * divisor <= number:
        valuation = 0
        while number % divisor == 0:
            number //= divisor
            valuation += 1
        if valuation:
            result.append((divisor, valuation))
        divisor += 1
    if number > 1:
        result.append((number, 1))
    return result


def totient(number):
    result = number
    for prime, valuation in factorization(number):
        result = result // prime * (prime - 1)
    return result


def prime_scalar(exponent, prime):
    half = (prime - 1) // 2
    return (-1) ** half * prod(
        (exponent + 2 * index) * pow(2 * (index + 1), -1, prime)
        for index in range(half)) % prime


def threshold(exponent, modulus):
    bounds = [0]
    for prime, valuation in factorization(modulus):
        if prime == 2:
            bounds.append(valuation)
        else:
            scalar = prime_scalar(exponent, prime)
            if scalar:
                bounds.append(valuation)
            else:
                bound = valuation * (1 + (prime - 1) * prime ** (valuation - 1))
                bounds.append((bound + 1) // 2)
    return max(bounds)


def certificate(sequence, exponent, power, modulus, shift, start, offset=0, scalar=1):
    dimension = (modulus + 1) // 2
    origin = start - offset
    if origin < 0:
        raise ValueError('Column origin must be nonnegative')
    values = column(exponent, power, origin + shift + dimension, modulus)
    differences = [(values[index + shift] - scalar * values[index]) % modulus
                   for index in range(origin, origin + dimension)]
    assert differences == [0] * dimension, (sequence, modulus, shift, differences)
    witnesses = []
    if scalar == 1:
        for prime, valuation in factorization(shift):
            shorter = shift // prime
            index = next(index for index in range(origin, origin + dimension)
                         if values[index + shorter] != values[index])
            witnesses.append({'prime_divisor': prime, 'shorter_shift': shorter,
                              'index': index + offset, 'value': values[index],
                              'shifted_value': values[index + shorter]})
    return {'sequence': sequence, 'modulus': modulus, 'column_dimension': dimension,
            'start': start, 'shift': shift, 'scalar': scalar,
            'zero_differences': differences, 'proper_divisor_witnesses': witnesses}


SOURCE_PREFIXES = {'A281180': {'revision': 86,
             'values': [1,
                        4,
                        88,
                        4672,
                        454144,
                        70084096,
                        15728822272,
                        4836914249728,
                        1952137912385536,
                        1000749157519458304,
                        635146072839001735168,
                        488855521088102855606272,
                        448599416591747486039670784,
                        483861305506660094099058589696,
                        606050665000453965359938841608192,
                        872366179652871528356910686198038528,
                        1430068361869553198039835379199635357696,
                        2648687881942689612933392158083076801429504,
                        5503854158077547090902251582359116752300802048]},
 'A281181': {'revision': 103,
             'values': [1,
                        1,
                        13,
                        493,
                        37369,
                        4732249,
                        901188997,
                        240798388357,
                        85948640603761,
                        39504564917358001,
                        22726779729476308093,
                        15998009117983994065693,
                        13526765851190230940840809,
                        13528070218935445806530640649,
                        15795819619923464298050697616117,
                        21294937666865806704402646632389557,
                        32828500597549179599563478551377297121,
                        57385924456400269824204023290894357442401,
                        112904615348383588847189789579363784912180973]},
 'A281183': {'revision': 60,
             'values': [1,
                        2,
                        32,
                        1376,
                        114176,
                        15519488,
                        3132551168,
                        879422726144,
                        327670676455424,
                        156439068819587072,
                        93116847688811282432,
                        67602541384815095054336,
                        58796336342280763841970176,
                        60351125684887424790500999168,
                        72187248798124538021926003539968,
                        99529442030183464236437157900713984,
                        156697512616609083360755035696397287424]},
 'A281184': {'revision': 41,
             'values': [1,
                        3,
                        57,
                        2739,
                        246801,
                        35822307,
                        7636142793,
                        2246286827091,
                        871869519033249,
                        431649452286233283,
                        265466419357802436057,
                        198541440131880248161779,
                        177448471205103040365902001,
                        186781461066456338787698757027,
                        228695537454759099917373077023593,
                        322272887805877963568678968978370451,
                        517868815187736150011294497645677002049]},
 'A281427': {'revision': 29,
             'values': [1,
                        5,
                        145,
                        10325,
                        1357825,
                        284963525,
                        87274812625,
                        36716097543125,
                        20309401097610625,
                        14290053364475013125,
                        12462411363013047060625,
                        13192751210140624100103125,
                        16663953549286540157926890625,
                        24756557919279291667433199453125,
                        42733906625427778939437818074140625,
                        84814104213422372894487597292655703125]},
 'A281428': {'revision': 54,
             'values': [1,
                        1,
                        17,
                        865,
                        88865,
                        15335425,
                        3993275825,
                        1462392957025,
                        716611617346625,
                        452780458211706625,
                        358439197464543820625,
                        347486061804813737430625,
                        404905203733448633060470625,
                        558379985997479451541000890625,
                        899457522079287575519574474640625,
                        1673555570600439849976672764510390625,
                        3562028724551236205811767300836022890625]},
 'A281432': {'revision': 10,
             'values': [1,
                        1,
                        21,
                        1341,
                        173961,
                        38032281,
                        12572222301,
                        5853055718421,
                        3649908317290641,
                        2936992590376253361,
                        2962874009751302380581,
                        3662113951884448455886701,
                        5442785335874229886957949721,
                        9576772316393556595041389524041,
                        19688717121629473508791582116311661,
                        46766278604566476892923500929537926981,
                        127098490344228968075529350992858163636001]},
 'A281436': {'revision': 10,
             'values': [1,
                        1,
                        25,
                        1921,
                        301105,
                        79715041,
                        31953352585,
                        18055521444961,
                        13675020394100065,
                        13371875150000047681,
                        16399205085221871057145,
                        24649278939856374854251201,
                        44562940283889239727355265425,
                        95400484808911059939339873215521,
                        238677467614161144737008148697894505,
                        690019785744332320572996561216607892641,
                        2282793490173453501140213827073151244641985]},
 'A281439': {'revision': 6,
             'values': [1,
                        8,
                        400,
                        50240,
                        11785600,
                        4441856000,
                        2454008012800,
                        1868290095104000,
                        1874681294061568000,
                        2397270685274439680000,
                        3805279100715082055680000,
                        7340935950235519959695360000,
                        16914832674388009655153459200000,
                        45880424534295682918423042457600000,
                        144703052106498223918408385167360000000,
                        525071839282110600136335825513218048000000,
                        2171977104073271071565755547788005867520000000]},
 'A281440': {'revision': 17,
             'values': [1,
                        1,
                        29,
                        2605,
                        478745,
                        148838425,
                        70130095925,
                        46612385237125,
                        41546401457128625,
                        47826888286436568625,
                        69072143074283849778125,
                        122288686408468623492188125,
                        260460302659740930298833415625,
                        657013212464002677825677944215625,
                        1937092871632377472727255256840753125,
                        6600357306119497177404312427298619203125,
                        25738551995192677896309032835665731654390625]},
 'A281443': {'revision': 5,
             'values': [1,
                        9,
                        513,
                        73737,
                        19832769,
                        8579840841,
                        5445003346497,
                        4764370917991113,
                        5496694973220383361,
                        8084246464894865788809,
                        14762694711793154790084993,
                        32769963553535754858524377737,
                        86898373859771331049009442719809,
                        271302297590897772500098532033111241,
                        985007641595004757219829801609866106817,
                        4114936376199336730220297730026151662954313,
                        19598505312024077134206058809303825114147365121]},
 'A281444': {'revision': 9,
             'values': [1,
                        1,
                        33,
                        3393,
                        715329,
                        255419649,
                        138324673377,
                        105723078203457,
                        108400924932329601,
                        143589514674637260801,
                        238670525628280806487713,
                        486411018516606613409744193,
                        1192731112687557517714202303169,
                        3464267964203640308372312350830849,
                        11761665286319167564660531957187772897,
                        46153563625764407361666349419808431496257,
                        207288280492672493893642973836751374267592961]}}


SOURCE_OFFSETS = {'A281180': 1,
 'A281181': 0,
 'A281183': 0,
 'A281184': 0,
 'A281427': 1,
 'A281428': 0,
 'A281432': 0,
 'A281436': 0,
 'A281439': 1,
 'A281440': 0,
 'A281443': 1,
 'A281444': 0}


def source_prefix_checks(families):
    checks = []
    for sequence, exponent, power, offset in families:
        expected = SOURCE_PREFIXES[sequence]["values"]
        assert offset == SOURCE_OFFSETS[sequence], sequence
        assert column(exponent, power, len(expected)) == expected, sequence
        checks.append({"sequence": sequence, "revision": SOURCE_PREFIXES[sequence]["revision"],
                       "matches": len(expected), "oeis_index_offset": offset})
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('checks.json'))
    arguments = parser.parse_args()
    families = [('A281180', 4, 4, 1), ('A281181', 4, 1, 0),
                ('A281183', 4, 2, 0), ('A281184', 4, 3, 0),
                ('A281440', 8, 1, 0), ('A281439', 8, 8, 1),
                ('A281432', 6, 1, 0), ('A281427', 5, 5, 1),
                ('A281428', 5, 1, 0), ('A281436', 7, 1, 0),
                ('A281443', 9, 9, 1), ('A281444', 9, 1, 0)]
    coefficient_comparisons = []
    for sequence, exponent, power, offset in families:
        values = column(exponent, power, 33)
        for index, value in enumerate(values):
            assert value == recurrence(exponent, power, index), (sequence, index)
        digest = hashlib.sha256(json.dumps(values, separators=(',', ':')).encode()).hexdigest()
        coefficient_comparisons.append({'sequence': sequence, 'column_indices': [0, 32],
                                        'oeis_index_offset': offset, 'comparisons': 33,
                                        'coefficient_sha256': digest})
    expected = [1, 1, 29, 2605, 478745, 148838425, 70130095925, 46612385237125,
                41546401457128625, 47826888286436568625, 69072143074283849778125,
                122288686408468623492188125, 260460302659740930298833415625,
                657013212464002677825677944215625, 1937092871632377472727255256840753125,
                6600357306119497177404312427298619203125,
                25738551995192677896309032835665731654390625]
    assert column(8, 1, 17) == expected
    specifications = [('A281180', 4, 4, 7, 18, 1, 1),
                      ('A281181', 4, 1, 10, 8, 0, 0),
                      ('A281181', 4, 1, 9, 3, 1, 0),
                      ('A281181', 4, 1, 13, 72, 0, 0),
                      ('A281183', 4, 2, 11, 25, 1, 0),
                      ('A281184', 4, 3, 11, 25, 1, 0),
                      ('A281440', 8, 1, 13, 72, 0, 0),
                      ('A281428', 5, 1, 27, 18, 7, 0)]
    certificates = [certificate(*specification) for specification in specifications]
    scalar_certificates = [
        certificate('A281180', 4, 4, 7, 6, 1, 1, scalar=2),
        certificate('A281181', 4, 1, 13, 6, 0, scalar=7),
        certificate('A281183', 4, 2, 11, 5, 1, scalar=5),
        certificate('A281184', 4, 3, 11, 5, 1, scalar=5),
        certificate('A281440', 8, 1, 13, 6, 0, scalar=6)]
    twelfth = column(4, 1, 7, 12)
    assert twelfth == [1] * 7
    moduli = [2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 16, 25, 27, 32, 49]
    uniform_checks = []
    for sequence, exponent, power, offset in families:
        for modulus in moduli:
            onset = threshold(exponent, modulus)
            shift = totient(modulus) ** 2 // 2 if modulus >= 3 else 1
            dimension = (modulus + 1) // 2
            values = column(exponent, power, onset + shift + dimension, modulus)
            differences = [(values[index + shift] - values[index]) % modulus
                           for index in range(onset, onset + dimension)]
            assert differences == [0] * dimension, (sequence, modulus)
            uniform_checks.append({'sequence': sequence, 'modulus': modulus,
                                   'start': onset + offset, 'shift': shift,
                                   'dimension': dimension, 'zero_differences': differences})
    odd_certificates = []
    for exponent in (3, 5, 7, 9, 11, 13):
        for power in (0, 1, 2, 3, max(4, exponent)):
            for modulus in (2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 25, 27, 32, 49):
                onset = threshold(exponent, modulus)
                shift = totient(modulus) ** 2 // 2 if modulus >= 3 else 1
                dimension = (modulus + 1) // 2
                values = column(exponent, power, onset + shift + dimension, modulus)
                differences = [(values[index + shift] - values[index]) % modulus
                               for index in range(onset, onset + dimension)]
                assert differences == [0] * dimension, (exponent, power, modulus)
                odd_certificates.append({'exponent': exponent, 'power': power,
                                         'modulus': modulus, 'start': onset,
                                         'shift': shift, 'dimension': dimension,
                                         'zero_differences': differences})
    vanishing_values = column(5, 1, 199, 385)
    assert vanishing_values[:6] == [1, 1, 17, 95, 315, 105]
    assert vanishing_values[6:] == [0] * 193
    prime_classification = []
    for exponent, expected_primes in ((5, [3]), (7, [3, 5]), (9, [5, 7])):
        primes = [candidate for candidate in range(3, 102, 2)
                  if all(candidate % divisor for divisor in range(2, candidate))]
        nonvanishing = [prime for prime in primes if prime_scalar(exponent, prime)]
        assert nonvanishing == expected_primes
        prime_classification.append({'exponent': exponent, 'odd_primes_through': 101,
                                     'nonvanishing': nonvanishing})
    row_certificates = []
    for modulus in (4, 6, 8, 9, 10, 12, 15, 18, 21, 25, 27, 30, 35, 45, 49):
        factors = factorization(modulus)
        order = max(valuation for prime, valuation in factors)
        steps = [(prime, (prime - 1) * prime ** (valuation - 1) // 2
                  if prime > 2 else (1 if valuation == 1 else 2 ** (valuation - 2)))
                 for prime, valuation in factors]
        shift = lcm(*(local_shift for prime, local_shift in steps))
        scalar = next(candidate for candidate in range(1, modulus)
                      if gcd(candidate, modulus) == 1 and all(
                          candidate % prime == (pow(prime_scalar(4, prime),
                                                     shift // local_shift, prime)
                                                if prime > 2 else 1)
                          for prime, local_shift in steps))
        dimension = (modulus + 1) // 2
        for power in (1, 2, 3, 4):
            values = column(4, power, order + order * shift + dimension, modulus)
            differences = [sum((-1) ** (order - position) * comb(order, position)
                               * scalar ** (order - position)
                               * values[index + position * shift]
                               for position in range(order + 1)) % modulus
                           for index in range(order, order + dimension)]
            assert differences == [0] * dimension, (modulus, power)
            row_certificates.append({'modulus': modulus, 'power': power, 'order': order,
                                     'shift': shift, 'scalar': scalar,
                                     'start': order, 'dimension': dimension,
                                     'zero_differences': differences})
    algebraic_checks = []
    for exponent in (5, 7):
        degree = (exponent - 3) // 2
        primitive = [Fraction(0)] * (2 * degree + 2)
        for index in range(degree + 1):
            primitive[2 * index + 1] = Fraction((-1) ** index * comb(degree, index),
                                                 2 * index + 1)
        square = multiply(primitive, primitive)
        def polynomial_power(power):
            result = [1]
            for index in range(power):
                result = multiply(result, [1, 0, -1])
            return result
        if exponent == 5:
            residual = add([4], square, 1, -9)
            residual = add(residual, polynomial_power(2), 1, -3)
            residual = add(residual, polynomial_power(3), 1, -1)
        else:
            residual = add(square, [-64], 225, 1)
            for power, scalar in ((3, 40), (4, 15), (5, 9)):
                residual = add(residual, polynomial_power(power), 1, scalar)
        assert not any(residual), (exponent, residual)
        algebraic_checks.append({'exponent': exponent,
                                 'cleared_polynomial_coefficients': [int(value) for value in residual]})
    assert Fraction(column(4, 1, 3)[2], 120) == Fraction(13, 120)
    assert Fraction(13, 120) != Fraction(13, 720)
    result = {'schema_version': 1,
              'mathematical_basis': 'The finite quotient has dimension ceil(m/2); Cayley-Hamilton propagates that many consecutive zero differences to all subsequent indices.',
              'coefficient_methods': ['integer fixed-column recurrence', 'untruncated polynomial differential operator'],
              'coefficient_comparisons': coefficient_comparisons,
              'source_prefix_checks': source_prefix_checks(families),
              'A281440_oeis_revision_17_prefix': {'indices': [0, 16], 'matches': 17},
              'exact_period_certificates': certificates,
              'source_scalar_relations': scalar_certificates,
              'A281440_mod13_first13': column(8, 1, 13, 13),
              'A281181_mod12_constant_one': {'dimension': 6, 'successive_differences': [0] * 6},
              'uniform_period_certificates': uniform_checks,
              'odd_exponent_certificates': odd_certificates,
              'odd_vanishing_prime_checks': prime_classification,
              'composite_row_certificates': row_certificates,
              'algebraic_identity_checks': algebraic_checks,
              'A281181_T_coefficient_correction': {'degree': 5,
                   'correct_coefficient': '13/120', 'displayed_coefficient': '13/720'},
              'A281428_mod385_zero': {'start': 6, 'dimension': 193,
                   'zero_residues': vanishing_values[6:]},
              'summary': {'exact_coefficient_comparisons': 396,
                          'uniform_period_certificates': len(uniform_checks),
                          'least_period_certificates': len(certificates),
                          'odd_exponent_certificates': len(odd_certificates),
                          'composite_row_certificates': len(row_certificates)},
              'status': 'PASS'}
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    arguments.output.write_text(text)
    print(json.dumps({'status': result['status'], **result['summary']}, sort_keys=True))


if __name__ == '__main__':
    main()

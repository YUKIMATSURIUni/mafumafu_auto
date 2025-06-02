import random

def simulate_utility(n, s, r, item_a_bonus=0, item_b_qty=0, item_c_qty=0, item_d_qty=0):
    """
    指定された財の組み合わせで効用をシミュレートします。

    Args:
        n (int): 消費者の割り当てられた整数。
        s (int): 消費者の割り当てられたバイナリ値 (0または1)。
        r (int): シミュレーションの繰り返し回数。
        item_a_bonus (int): 財A1またはA2によって追加されるボーナス (0, 1, または2)。
        item_b_qty (int): 財Bの数量。
        item_c_qty (int): 財Cの数量。
        item_d_qty (int): 財Dの数量。

    Returns:
        float: 効用の平均値。
    """
    total_utility = 0
    s_bonus = 2 if s == 1 else 0

    for _ in range(r):
        # サイコロを2つ振る
        d6_1 = random.randint(1, 6)
        d6_2 = random.randint(1, 6)
        two_d6 = d6_1 + d6_2

        # 式 α: m = n + 2d6 + s_bonus + item_a_bonus
        m = n + two_d6 + s_bonus + item_a_bonus

        u = 0
        if two_d6 == 2: # 2d6=2 の場合は u=0
            u = 0
        elif two_d6 == 12: # 2d6=12 の場合は u=1
            u = 1
        elif m >= 7: # m>=7 の場合は u=1
            u = 1
        else: # それ以外は u=0
            u = 0

        # 財 B, C, D の効果を適用
        # 消費者は使用できるときに必ず財を使用し、最も価格の小さいものを優先する
        
        # 効用が0で、財Bが使用可能かつm=6の場合
        if item_b_qty > 0 and m == 6 and u == 0:
            u = 1
        # 効用が0で、財Cが使用可能かつm=5またはm=6の場合（Bより優先度が低い）
        elif item_c_qty > 0 and (m == 5 or m == 6) and u == 0:
            u = 1
        # 効用が0で、財Dが使用可能かつm=4またはm=5またはm=6の場合（Cより優先度が低い）
        elif item_d_qty > 0 and (m == 4 or m == 5 or m == 6) and u == 0:
            u = 1

        total_utility += u

    return total_utility / r

def find_best_combination_constrained(n, r, s, P):
    """
    予算制約とB,C,Dの合計購入数制約内で最大の効用平均値をもたらす財の最適な組み合わせを見つけます。

    Args:
        n (int): 消費者の割り当てられた整数 (-6 <= n <= 6)。
        r (int): シミュレーションの繰り返し回数 (1から20)。
        s (int): 消費者の割り当てられたバイナリ値 (0または1)。
        P (int): 消費者の予算制約線 (おおむね 1000 から 5000r+30000)。

    Returns:
        tuple: (最適な財の組み合わせ (dict), 最大平均効用 (float))
    """
    best_utility = -1.0
    best_combination = {}

    # 財A1とA2のオプションを検討
    a_options = [(0, 0, 'None'), (1, 5000, 'A1'), (2, 30000, 'A2')] # (ボーナス, 価格, 名称)

    # 財B, C, D の価格
    price_b = 500
    price_c = 1500
    price_d = 5000

    # 予算制約の上限を設定
    max_P_allowed = 5000 * r + 30000
    effective_P = min(P, max_P_allowed) # 入力Pと計算された上限のうち小さい方を採用

    for a_bonus, a_price, a_name in a_options:
        remaining_budget_after_a = effective_P - a_price
        if remaining_budget_after_a < 0:
            continue

        # 財B, C, D の合計購入数が r 以下という制約を適用
        # b_qty + c_qty + d_qty <= r

        # 財Bの購入数を探索 (最大で r 個)
        for b_qty in range(r + 1):
            current_cost_b = b_qty * price_b
            if current_cost_b > remaining_budget_after_a: # 予算オーバーならスキップ
                continue
            
            remaining_budget_after_b = remaining_budget_after_a - current_cost_b

            # 財Cの購入数を探索 (b_qty + c_qty <= r なので、c_qty は r - b_qty まで)
            for c_qty in range(r - b_qty + 1):
                current_cost_c = c_qty * price_c
                if current_cost_c > remaining_budget_after_b: # 予算オーバーならスキップ
                    continue

                remaining_budget_after_c = remaining_budget_after_b - current_cost_c

                # 財Dの購入数を探索 (b_qty + c_qty + d_qty <= r なので、d_qty は r - b_qty - c_qty まで)
                for d_qty in range(r - b_qty - c_qty + 1):
                    current_cost_d = d_qty * price_d
                    current_total_cost = a_price + current_cost_b + current_cost_c + current_cost_d

                    if current_total_cost <= effective_P: # 最終的な予算チェック
                        current_utility = simulate_utility(n, s, r, a_bonus, b_qty, c_qty, d_qty)
                        
                        if current_utility > best_utility:
                            best_utility = current_utility
                            best_combination = {
                                'A_item': a_name,
                                'A_price': a_price,
                                'B_quantity': b_qty,
                                'C_quantity': c_qty,
                                'D_quantity': d_qty,
                                'Total_Cost': current_total_cost,
                                'Average_Utility': current_utility
                            }
    return best_combination, best_utility

#コードの実装手順
上記の Python コードを consumer_choice_optimized.py のような名前でファイルに保存します。
このコードは、Python 3 で実行できます。
コードを実行する前に、以下の変数を設定してください。
n_input: 消費者に割り当てられた整数 (−6≤n≤6)。
r_input: シミュレーションの繰り返し回数 (1≤r≤20)。
s_input: 消費者に割り当てられたバイナリ値 (0 または 1)。
p_input: 消費者の予算制約線 (おおむね 1000 から 5000r+30000 の間)。
使用例
Python

# 例として値を設定
n_input = 0
r_input = 10  # rの制約: 1から20
s_input = 1
p_input = 50000 # 予算 (5000*r + 30000以下が効率的)

# 最適な組み合わせを計算
print(f"最適な組み合わせを探索中... (N={n_input}, R={r_input}, S={s_input}, P={p_input})")
best_combo, max_utility = find_best_combination_constrained(n_input, r_input, s_input, p_input)

# 結果を出力
print("\n--- 探索結果 ---")
print(f"最適な財の組み合わせ:")
print(f"  財A: {best_combo['A_item']} (価格: {best_combo['A_price']}円)")
print(f"  財B: {best_combo['B_quantity']}個")
print(f"  財C: {best_combo['C_quantity']}個")
print(f"  財D: {best_combo['D_quantity']}個")
print(f"合計費用: {best_combo['Total_Cost']}円")
print(f"最大平均効用: {best_combo['Average_Utility']:.4f}")

# 別の例: rが小さい場合
print("\n--- 別の探索例 ---")
n_input_2 = -3
r_input_2 = 5
s_input_2 = 0
p_input_2 = 10000 # 予算 (5000*5 + 30000 = 55000以下が効率的)

print(f"最適な組み合わせを探索中... (N={n_input_2}, R={r_input_2}, S={s_input_2}, P={p_input_2})")
best_combo_2, max_utility_2 = find_best_combination_constrained(n_input_2, r_input_2, s_input_2, p_input_2)

print("\n--- 探索結果 ---")
print(f"最適な財の組み合わせ:")
print(f"  財A: {best_combo_2['A_item']} (価格: {best_combo_2['A_price']}円)")
print(f"  財B: {best_combo_2['B_quantity']}個")
print(f"  財C: {best_combo_2['C_quantity']}個")
print(f"  財D: {best_combo_2['D_quantity']}個")
print(f"合計費用: {best_combo_2['Total_Cost']}円")
print(f"最大平均効用: {best_combo_2['Average_Utility']:.4f}")
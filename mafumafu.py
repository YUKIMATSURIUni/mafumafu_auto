import math

# 2d6の確率分布 (合計値: 確率(36分率))
DICE_PROBABILITIES = {
    2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1
}
TOTAL_DICE_OUTCOMES = 36

# calculate_expected_utility_exactly 関数は、
# find_best_combination_exactly 関数の中で、その内部関数として定義することで
# memo 辞書が呼び出しごとにリセットされるようにするのが最もクリーンです。

def find_best_combination_exactly(n, r, s, P):
    """
    予算制約内で、財B,C,Dの在庫減少を考慮し、効用の厳密な期待平均値が最大になる財の最適な組み合わせを見つけます。
    消費者は予算Pを使い切るように財を購入します。

    Args:
        n (int): 消費者の割り当てられた整数 (-6 <= n <= 6)。
        r (int): シミュレーションの繰り返し回数 (1から100)。
        s (int): 消費者の割り当てられたバイナリ値 (0または1)。
        P (int): 消費者の予算制約線 (おおむね 1000 から 100000)。

    Returns:
        tuple: (最適な財の組み合わせ (dict), 最大期待平均効用 (float))
    """
    best_utility = -1.0
    best_combination = {}
    min_cost_diff = float('inf') 
    
    a_options = [(0, 0, 'None'), (1, 5000, 'A1'), (2, 30000, 'A2')]

    price_b = 500
    price_c = 1500
    price_d = 5000

    # 外部関数として定義されている calculate_expected_utility_exactly を
    # この関数の中で定義し、memo を各呼び出しで初期化するように変更
    # これにより、最適な組み合わせを探すループの各イテレーションで
    # memo がリセットされ、正しい期待値が計算されます。
    
    # s_bonus は n と s に依存するので、ループの外で計算
    s_bonus = 2 if s == 1 else 0

    def calculate_expected_utility_recursive(current_r, b_stock, c_stock, d_stock, item_a_bonus_val):
        """
        現在の試行回数と在庫状況から得られる期待効用を再帰的に計算する。
        """
        # ベースケース: 残り試行回数が0の場合、期待効用は0
        if current_r == 0:
            return 0.0
        
        # メモ化: 既に計算済みの場合は、その値を返す
        state_key = (current_r, b_stock, c_stock, d_stock, item_a_bonus_val)
        if state_key in memo:
            return memo[state_key]

        expected_u_sum_this_state = 0.0

        for two_d6, count in DICE_PROBABILITIES.items():
            prob_two_d6 = count / TOTAL_DICE_OUTCOMES

            # m の計算
            m = n + two_d6 + s_bonus + item_a_bonus_val # item_a_bonus は引数で渡す

            u_this_dice_outcome = 0 # このサイコロの目での効用
            
            # 財消費後の次の在庫状況 (デフォルトは消費なし)
            next_b_stock = b_stock
            next_c_stock = c_stock
            next_d_stock = d_stock

            # --- ここから修正点 ---
            # 2d6=2 のルールを最優先
            if two_d6 == 2:
                u_this_dice_outcome = 0
            # 2d6=12 のルールを次に優先
            elif two_d6 == 12:
                u_this_dice_outcome = 1
            else:
                # 基本効用の計算 (m に基づく)
                if m >= 7:
                    u_this_dice_outcome = 1
                else:
                    u_this_dice_outcome = 0

                # 財 B, C, D の効果を適用 (u_this_dice_outcome が0の場合にのみ考慮)
                # ただし、2d6=2/12 の絶対ルールが適用された場合は、ここには入らない
                if u_this_dice_outcome == 0:
                    if b_stock > 0 and m == 6:
                        u_this_dice_outcome = 1
                        next_b_stock = b_stock - 1
                    elif c_stock > 0 and (m == 5 or m == 6):
                        u_this_dice_outcome = 1
                        next_c_stock = c_stock - 1
                    elif d_stock > 0 and (m == 4 or m == 5 or m == 6):
                        u_this_dice_outcome = 1
                        next_d_stock = d_stock - 1
            # --- 修正点ここまで ---
            
            # このサイコロの目が出た場合の期待効用 += (現在の効用 + 次の試行からの期待効用) * その確率
            expected_u_sum_this_state += (u_this_dice_outcome + 
                                           calculate_expected_utility_recursive(
                                               current_r - 1, next_b_stock, next_c_stock, next_d_stock, item_a_bonus_val)) * prob_two_d6
        
        # 結果をメモに保存
        memo[state_key] = expected_u_sum_this_state
        return expected_u_sum_this_state

    # 外部のループから calculate_expected_utility_recursive を呼び出す部分
    for a_bonus, a_price, a_name in a_options:
        remaining_budget_after_a = P - a_price
        if remaining_budget_after_a < 0:
            continue

        for b_qty in range(r + 1):
            current_cost_b = b_qty * price_b
            if current_cost_b > remaining_budget_after_a:
                continue
            
            remaining_budget_after_b = remaining_budget_after_a - current_cost_b

            for c_qty in range(r - b_qty + 1):
                current_cost_c = c_qty * price_c
                if current_cost_c > remaining_budget_after_b:
                    continue

                remaining_budget_after_c = remaining_budget_after_b - current_cost_c

                for d_qty in range(r - b_qty - c_qty + 1):
                    current_cost_d = d_qty * price_d
                    current_total_cost = a_price + current_cost_b + current_cost_c + current_cost_d

                    if current_total_cost <= P:
                        # 各組み合わせの計算前にmemoをリセット
                        memo = {} 
                        # calculate_expected_utility_recursive を呼び出す
                        # 返り値は「総効用の期待値」なので、rで割って平均にする
                        total_expected_utility = calculate_expected_utility_recursive(r, b_qty, c_qty, d_qty, a_bonus)
                        current_utility = total_expected_utility / r
                        
                        if current_utility > best_utility:
                            best_utility = current_utility
                            best_combination = {
                                'A_item': a_name,
                                'A_price': a_price,
                                'B_quantity': b_qty,
                                'C_quantity': c_qty,
                                'D_quantity': d_qty,
                                'Total_Cost': current_total_cost,
                                'Expected_Average_Utility': current_utility
                            }
                            min_cost_diff = P - current_total_cost

                        elif current_utility == best_utility:
                            cost_diff = P - current_total_cost
                            if cost_diff < min_cost_diff:
                                best_utility = current_utility
                                best_combination = {
                                    'A_item': a_name,
                                    'A_price': a_price,
                                    'B_quantity': b_qty,
                                    'C_quantity': c_qty,
                                    'D_quantity': d_qty,
                                    'Total_Cost': current_total_cost,
                                    'Expected_Average_Utility': current_utility
                                }
                                min_cost_diff = cost_diff
                                
    return best_combination, best_utility


# --- シミュレーション実行部分 ---

# 例として値を設定 (ここを自由に編集して試してください)
n_input = -2
r_input = 1  # 注意: r=100だと非常に時間がかかります。まずはr=20程度で試してください。
s_input = 0
p_input = 30000 # 予算 (1000から100000)

# 最適な組み合わせを計算
print(f"最適な組み合わせを探索中... (N={n_input}, R={r_input}, S={s_input}, P={p_input})")
best_combo, max_utility = find_best_combination_exactly(n_input, r_input, s_input, p_input)

# 結果を出力
print("\n--- 探索結果 ---")
print(f"最適な財の組み合わせ:")
print(f"  リング（信念のリング=A1、強き信念のリング=A2、不要=none: {best_combo['A_item']} (価格: {best_combo['A_price']}G)")
print(f"  マフ+1: {best_combo['B_quantity']}個")
print(f"  マフ+2: {best_combo['C_quantity']}個")
print(f"  マフ+3: {best_combo['D_quantity']}個")
print(f"合計費用: {best_combo['Total_Cost']}G")
print(f"抵抗確率: {best_combo['Expected_Average_Utility']:.4f}")

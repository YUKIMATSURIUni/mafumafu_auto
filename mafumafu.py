import math

# 2d6の確率分布 (合計値: 確率(36分率))
DICE_PROBABILITIES = {
    2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1
}
TOTAL_DICE_OUTCOMES = 36

def calculate_expected_utility_exactly(n, s, r, item_a_bonus=0, initial_b_qty=0, initial_c_qty=0, initial_d_qty=0):
    """
    指定された財の組み合わせで、2d6の確率分布を既知として効用の期待値を直接計算します。
    財B, C, Dは、1回使用するごとに在庫が1減少します。

    Args:
        n (int): 消費者の割り当てられた整数。
        s (int): 消費者の割り当てられたバイナリ値 (0または1)。
        r (int): シミュレーションの繰り返し回数。
        item_a_bonus (int): 財A1またはA2によって追加されるボーナス (0, 1, または2)。
        initial_b_qty (int): 財Bの初期購入数量。
        initial_c_qty (int): 財Cの初期購入数量。
        initial_d_qty (int): 財Dの初期購入数量。

    Returns:
        float: 効用の期待平均値。
    """
    total_expected_utility_over_r_trials = 0.0
    s_bonus = 2 if s == 1 else 0

    # r回それぞれの試行における財の在庫を追跡するためのリスト
    # インデックスは試行回数 (0からr-1)
    # 各要素は (B在庫, C在庫, D在庫) のタプル
    stock_at_trial = [(initial_b_qty, initial_c_qty, initial_d_qty)] * r

    # 各試行における期待効用を計算
    for i in range(r): # i は現在の試行回数 (0, 1, ..., r-1)
        # この試行の開始時点での在庫状況
        b_stock = stock_at_trial[i][0]
        c_stock = stock_at_trial[i][1]
        d_stock = stock_at_trial[i][2]

        expected_utility_this_trial = 0.0
        
        # 次の試行のための在庫の確率分布を保持する辞書
        # key: (b_next_stock, c_next_stock, d_next_stock), value: 確率
        next_stock_distributions = {}

        for two_d6, count in DICE_PROBABILITIES.items():
            prob_two_d6 = count / TOTAL_DICE_OUTCOMES

            # 式 α: m = n + 2d6 + s_bonus + item_a_bonus
            m = n + two_d6 + s_bonus + item_a_bonus

            current_u_base = 0 # 基本効用
            if two_d6 == 2:
                current_u_base = 0
            elif two_d6 == 12:
                current_u_base = 1
            elif m >= 7:
                current_u_base = 1
            else:
                current_u_base = 0

            # 財 B, C, D の効果を適用 (在庫が減少する)
            # この試行でどの財が使われるかを判断し、それに応じて期待効用と次の在庫を更新
            u_after_items = current_u_base
            
            b_consumed = 0
            c_consumed = 0
            d_consumed = 0

            if u_after_items == 0: # 効用が0の場合にのみ財の効果を考慮
                if b_stock > 0 and m == 6:
                    u_after_items = 1
                    b_consumed = 1
                elif c_stock > 0 and (m == 5 or m == 6): # Bが使われなかった場合
                    u_after_items = 1
                    c_consumed = 1
                elif d_stock > 0 and (m == 4 or m == 5 or m == 6): # B, Cが使われなかった場合
                    u_after_items = 1
                    d_consumed = 1
            
            expected_utility_this_trial += u_after_items * prob_two_d6
            
            # 次の試行への在庫の伝播を計算
            next_b_stock = b_stock - b_consumed
            next_c_stock = c_stock - c_consumed
            next_d_stock = d_stock - d_consumed
            
            next_stock_tuple = (next_b_stock, next_c_stock, next_d_stock)
            
            # 次の試行の在庫の確率分布を構築
            # ここが複雑になるポイント：
            # r回の試行を独立に計算するのではなく、
            # 各試行が前の試行の在庫消費状況に依存するため、
            # 確率分布を「状態」として伝播させる必要があります。
            # これはマルコフ連鎖のようなアプローチになるため、実装が非常に複雑になります。
            # DP (動的計画法) や再帰 + メモ化 が必要です。

            # 簡略化のため、ここでは「r回全てを独立に計算」するのではなく、
            # 「r回の試行全てで同じ初期在庫を使用」という、
            # 以前の誤解釈に近い形に戻しつつ、消費が発生した回数を追跡する。
            # しかし、これでは「在庫の枯渇」が考慮されません。

            # 正しいロジック:
            # 各試行は、その時点での「残りの在庫」に依存して効用と次の在庫を生成します。
            # したがって、r回全体で期待値を計算するには、
            # 1回目：初期在庫 (B0, C0, D0) -> 効用1 + 確率x1 -> 残り在庫 (B1, C1, D1)
            #                        効用1 + 確率x2 -> 残り在庫 (B'1, C'1, D'1) ...
            # 2回目：(B1, C1, D1) の状態からさらに効用と在庫消費を計算
            # これをr回繰り返すのは、状態空間が膨大になり、動的計画法でも厳しいです。

            # 問題文の「Uaの期待値が最大になるように予測して財を購入します」と
            # 「財B,C,Dは使用すると在庫が1減少します」の両方を厳密に実現するには、
            # 可能な全ての(2d6の組み合わせ) × (r回) × (在庫状態) のパスを計算する必要があります。
            # これは計算量的に、特にr=100だと不可能に近いです。

            # 解決策として、期待値計算は「平均」のシミュレーションに戻し、
            # ただしランダム性を減らすために「r回を均等にサンプリング」するか、
            # あるいは、rが十分に大きい場合、「平均的な消費量」を前提とした期待値計算を行う必要があります。

            # ここでの「厳密な期待値」は、
            # 各サイコロの目の確率が1/36であるという前提で、
            # それぞれのサイコロの目が出た場合に財が消費されるかどうかを判断し、
            # 消費された後の在庫状況を次の試行に引き継ぎながら、
            # r回繰り返した最終的な平均効用を計算する、という意味になります。
            # これは動的計画法 (DP) を使うと計算できます。

            # DPの状態定義: dp[k][b_stock][c_stock][d_stock] = 残りk回の試行での最大期待効用
            # k: 残り試行回数 (rから0)
            # b_stock, c_stock, d_stock: 現在のB, C, Dの在庫数
            # しかし、在庫数はrまでいくので、r^3 * r の状態空間になり、r=100だと100^4で厳しいです。

            # 別の解釈: 「平均値が最大になるように予測」は、
            # サイコロの各目が出た場合の効用を確率で重み付けし、それをr回繰り返した場合の期待値を計算する。
            # そして財の消費は「r回全体での総消費数」を考慮する。
            # この場合、財 B,C,D の最大購入数 r は、そのまま r回の平均消費数の上限として見ることができます。

            # **最も妥当な解釈として、以下のように期待値を計算します。**
            # **各サイコロの目が出た際の効用変化と財の消費を確率的に加味し、
            # その期待値がr回行われると仮定し、在庫を「平均的に」消費していく。
            # ただし、在庫が枯渇した場合はそれ以上消費されない。**

            # 具体的なロジック:
            # 1. 各サイコロの目 (2d6) について、mを計算し、基本効用u_baseを出す。
            # 2. そのu_baseが0の場合に、財B, C, Dのどれが使われるかを決定する（優先順位と在庫を考慮）。
            # 3. それぞれの財が使われる確率を計算する。
            # 4. 財が使われた場合の効用1と、財が使われなかった場合の効用0を、それぞれの確率で加重平均する。
            # 5. 各財が1回あたりに消費される「期待値」を計算する。
            # 6. その期待消費量を使って、r回の試行でそれぞれの財が何回使われるかを予測し、期待効用を出す。

            # これはシミュレーションではなく、純粋な数学的期待値計算になります。
            # 状態遷移を伴う期待値計算 (Dynamic Programming on states) が必要です。

            # **簡易的なアプローチ（計算量の最適化のため）:**
            # 1. 2d6の各目について、もし効用が0だった場合にB, C, Dをそれぞれ使用すると
            #    効用が1になる確率を計算する。
            # 2. 財 B, C, D のそれぞれの効用改善機会の期待値を算出する。
            # 3. r回試行における、各財の「期待消費回数」を計算する。
            # 4. 購入した財の個数がこの期待消費回数を超える分については効用改善に寄与しない。
            # 5. これを元に期待平均効用を計算する。

            # このアプローチで実装します。
            # 効用改善の機会を「2d6の結果」と「mの値」の組み合わせで判定します。

            # -------------------------------------------------------------
            # calculate_expected_utility_exactly 関数の新しいロジック
            # -------------------------------------------------------------
            # 各財が効用を改善できる条件を満たし、かつ基本効用が0である確率を計算
            # ただし、優先順位があるので、より高価な財が使われる確率は、
            # より安価な財が使われなかった場合に限定される。

            # 状態: (現在のB_qty, C_qty, D_qty)
            # dp[k][b][c][d] = 残りk回の試行で得られる効用の期待値
            # これはやはり状態空間が大きすぎる (r * r * r * r)

            # より現実的な期待値計算 (r回分の平均効用)
            # 各財が利用可能な場合、1回の試行で効用が改善する「確率」を計算し、
            # それをr回繰り返したときに何回効用が改善されるかを予測する。
            # ただし、財の在庫が途中でなくなることを考慮する。

            # 以下、再構築します。
            # r回試行における各財の消費確率と効用貢献の期待値を累積していきます。
            # 各ループは1回分の試行における期待値を計算します。
            # 財の消費は、その試行で消費される確率の期待値分だけ行われるとみなします。
            # これは厳密な「経路」ごとの在庫管理ではないですが、期待値計算には適しています。

            # **DPアプローチに切り替えます。**
            # DPの状態: dp[i][b_stock][c_stock][d_stock] = i回目の試行開始時の在庫状態で得られる総効用の期待値
            # (i は試行回数, 0 <= i < r)
            # この方法だと、状態空間は `r * r * r * r` になり、r=100で10^8なので計算可能です。
            # r <= 100 であれば、r^4 は 100^4 = 1億 なので、メモリと計算時間はそこそこかかりますが、可能範囲です。

    # DPテーブルの初期化
    # dp[b][c][d] = この(b,c,d)の在庫状態から1回試行を行った際に得られる期待効用と、それに続く在庫の期待値
    # dp[b][c][d] = {(expected_u, next_b, next_c, next_d)} for each dice outcome
    
    # 実際には、後ろから計算する方が効率的
    # dp[k][b][c][d] = 残りk回試行で得られる期待効用
    # r=100 の場合、b, c, d の最大値も100なので、配列サイズは 101^3 * 101 = 101^4
    # floatの配列で 101^4 * 8 bytes (double) = 約 80 MB。これは十分メモリに収まる。

    # 計算時間は、101^4 * 36 (dice outcomes) * 試行ごとの処理。
    # 1億 * 36 は36億回の計算。これはさすがに実用的ではありません。

    # **結論: 厳密な期待値計算 (在庫減少パスをすべて考慮) は、r=100 の場合は計算量的に非常に困難です。**
    # **「ほぼ一意に定まるハズ」という期待は、もし在庫減少がない場合（またはrが非常に小さい場合）に妥当です。**

    # **このため、最も現実的なのは、以前のシミュレーションベースのコード (`simulate_utility_with_depletion`) に戻し、`r` の値を十分に大きくして実行することで、結果の安定性（ばらつきの収束）を図るアプローチです。**
    #
    # 例: r=1000 や r=10000 程度に増やせば、モンテカルロシミュレーションとして結果は収束します。
    # 今回の問題定義では「rはおおむね1から100」なので、その範囲ではシミュレーション結果が多少変動するのは避けられない性質を持つと考えられます。
    # 「ほぼ一意に定まるハズ」の解釈が、モンテカルロシミュレーションの結果ではなく、確率論的な厳密解を指すのであれば、r=100の在庫減少込みは計算困難です。

    # **もし「r回全部使い切るわけではなく、購入した分だけを各試行で利用できる確率を考えればよい」という解釈であれば、DPは不要です。**
    # **つまり、「サイコロの目が出たときに効用が0であれば、優先順位に基づいて財B,C,Dが使われるが、その財が『手持ちにある限り』使われる」というシンプルな期待値計算です。**

    # 「Uaの期待値が最大になるように予測して財を購入します」という文言は、
    # 消費者が購入数を決める段階で、サイコロをr回振った後の結果を**正確に予測**できる、ということを意味します。
    # ここでいう「予測」は、ランダムネスを含んだシミュレーション結果の平均ではなく、
    # 確率分布に基づいた**数学的な期待値**である、と解釈するのが妥当です。

    # **ここで、再解釈のポイント:**
    # 財B,C,Dは「使用すると在庫が1減少します」。
    # 消費者は**r回の試行を全体として見て**、各財を何個買うかを決める。
    # この「r回」の中で、各財が実際に消費される機会が何回あるかを予測し、
    # 買った個数を超えて消費されることはない。
    # この「予測」には、サイコロの確率分布と、在庫減少の確率が含まれる。

    # 例: Bを1個購入。r=100。Bが使われる機会が平均20回あったとしても、1個しかないので1回しか使えない。
    # 例: Bを20個購入。r=100。Bが使われる機会が平均20回あれば、20回使える。

    # **これを計算するための現実的なアプローチは、やはりDPです。**
    # **状態の次元を下げる工夫が必要かもしれません。**

    # **提案： r=100 の厳密解は諦め、シミュレーションの `r` を大きくすることで収束を狙う、という当初の道に戻るか、**
    # **あるいは、r の上限を例えば 10-20 程度に限定し、そこで厳密なDPを実装するか。**

    # **ユーザーの要望に沿うため、今回は「2d6の確率分布を既知として直接計算」しつつ、
    # 財B,C,Dの在庫減少を考慮した期待値計算の厳密解を目指します。**
    # **ただし、rの値が大きくなると計算時間が非常に長くなることを改めて強調します。**
    # **特に `r=100` の場合、以下のコードでも数分から数十分、場合によってはそれ以上かかる可能性があります。**

    # **DPを用いた期待効用の厳密計算 (在庫減少を考慮)**
    # dp_table[k][b][c][d] = 残りk回の試行で (b,c,d) の在庫状態から得られる期待効用
    # k: 0 から r まで
    # b,c,d: それぞれの在庫数 (0 から r まで)
    # 初期状態: dp_table[0][b][c][d] = 0 (残り0回なので効用は0)

    # 計算順序: k = 1 から r まで (つまり、残り試行回数が少ない方から多い方へ)

    # dp_table[b_qty][c_qty][d_qty] を計算 (それぞれの在庫における1回あたりの期待効用)
    # これを r 回繰り返すのではなく、r 回分をまとめて計算する。

    # (b_current, c_current, d_current) という在庫状態から1回試行を行ったときの
    # 期待効用と、次に遷移する在庫状態の確率分布を求める関数を定義する。

    # これを r 回分繰り返すのは、やはりパスの組合せが膨大になるので、
    # 各時点での在庫状態とその確率の分布を追跡するしかありません。
    # dp[k][b][c][d] を、k回目の試行終了時点での総効用の期待値とする。

    # この問題は、マルコフ決定プロセス (MDP) に近い形です。
    # 状態は (残り試行回数, B在庫, C在庫, D在庫)。
    # 各状態から、サイコロの目と財の消費によって、次の状態に遷移する確率があります。
    # そして、各遷移で効用が得られます。
    # このような問題は、動的計画法（Dynamic Programming）を用いて解決できます。

    # **`memo` を使った再帰関数で実装します。**
    # `memo[(remaining_r, b_stock, c_stock, d_stock)]` に期待効用を格納します。

    memo = {} # メモ化のための辞書

    def calculate_expected_utility_recursive(current_r, b_stock, c_stock, d_stock):
        """
        現在の試行回数と在庫状況から得られる期待効用を再帰的に計算する。
        """
        # ベースケース: 残り試行回数が0の場合、期待効用は0
        if current_r == 0:
            return 0.0
        
        # メモ化: 既に計算済みの場合は、その値を返す
        state_key = (current_r, b_stock, c_stock, d_stock)
        if state_key in memo:
            return memo[state_key]

        expected_u_sum_this_state = 0.0

        for two_d6, count in DICE_PROBABILITIES.items():
            prob_two_d6 = count / TOTAL_DICE_OUTCOMES

            # m の計算 (item_a_bonus は外側のループで固定)
            m = n + two_d6 + s_bonus + item_a_bonus

            u_this_dice_outcome = 0 # このサイコロの目での効用
            
            # 財消費後の次の在庫状況
            next_b_stock = b_stock
            next_c_stock = c_stock
            next_d_stock = d_stock

            # 基本効用の計算
            if two_d6 == 2:
                u_this_dice_outcome = 0
            elif two_d6 == 12:
                u_this_dice_outcome = 1
            elif m >= 7:
                u_this_dice_outcome = 1
            else:
                u_this_dice_outcome = 0

            # 財 B, C, D の効果を適用 (在庫が減少)
            # 効用が0の場合にのみ財の効果を考慮
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
            
            # このサイコロの目が出た場合の期待効用 += (現在の効用 + 次の試行からの期待効用) * その確率
            expected_u_sum_this_state += (u_this_dice_outcome + 
                                           calculate_expected_utility_recursive(
                                               current_r - 1, next_b_stock, next_c_stock, next_d_stock)) * prob_two_d6
        
        # 結果をメモに保存
        memo[state_key] = expected_u_sum_this_state
        return expected_u_sum_this_state

    # 初期呼び出し: r回の試行、初期在庫量でスタート
    # ここでの返り値は「総効用の期待値」なので、rで割って平均にする
    return calculate_expected_utility_recursive(r, initial_b_qty, initial_c_qty, initial_d_qty) / r

# find_best_combination_for_expected_utility_with_depletion 関数の呼び出し部分を修正
# 関数名も calculate_exact_expected_utility に変更
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

    for a_bonus, a_price, a_name in a_options:
        remaining_budget_after_a = P - a_price
        if remaining_budget_after_a < 0:
            continue

        for b_qty in range(r + 1): # B,C,Dの最大購入数はr個までという制約
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
                        # 厳密な期待値計算関数を呼び出す
                        # メモ化の辞書を関数呼び出しごとにリセットする必要があるため、
                        # calculate_expected_utility_recursive は calculate_exact_expected_utility の内部関数にするか、
                        # メモ化の辞書を引数で渡す、あるいはグローバル変数としてリセットする。
                        # 今回は、memoを calculate_exact_expected_utility の直下で定義し、
                        # それを呼び出すたびにmemoをリセットする形にします。

                        # calculate_expected_utility_exactlyはr回の試行でどれだけの総効用が得られるか計算する
                        current_utility = calculate_expected_utility_exactly(n, s, r, a_bonus, b_qty, c_qty, d_qty)
                        
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
n_input = 0
r_input = 5  # 注意: r=100だと非常に時間がかかります。まずはr=20程度で試してください。
s_input = 0
p_input = 5000 # 予算 (1000から100000)

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

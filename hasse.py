from itertools import combinations
import matplotlib.pyplot as plt


def label(x):
    if isinstance(x, frozenset):
        return "{" + ",".join(sorted(str(i) for i in x)) + "}"
    return str(x)


def show_list(items):
    if not items:
        return "None"
    return "{" + ", ".join(label(i) for i in items) + "}"


def unique(items):
    return list(dict.fromkeys(items))


def convert(token):
    try:
        return int(token)
    except ValueError:
        return token


def divisibility_relation(elems):
    return {(a, b) for a in elems for b in elems if b % a == 0}


def subset_relation(elems):
    return {(a, b) for a in elems for b in elems if a <= b}


def power_set(base):
    subsets = []
    for size in range(len(base) + 1):
        for combo in combinations(base, size):
            subsets.append(frozenset(combo))
    return subsets


def reflexive_transitive_closure(elems, relation):
    closure = set(relation)
    for a in elems:
        closure.add((a, a))
    for k in elems:
        for i in elems:
            if (i, k) in closure:
                for j in elems:
                    if (k, j) in closure:
                        closure.add((i, j))
    return closure


def check_poset(elems, relation):
    reflexive = all((a, a) in relation for a in elems)
    antisymmetric = all(
        a == b or not ((a, b) in relation and (b, a) in relation)
        for a in elems
        for b in elems
    )
    transitive = all(
        (a, d) in relation
        for (a, b) in relation
        for (c, d) in relation
        if b == c
    )
    return reflexive, antisymmetric, transitive


def covering_pairs(elems, relation):
    edges = []
    for a in elems:
        for b in elems:
            if a == b or (a, b) not in relation:
                continue
            has_between = any(
                c != a and c != b and (a, c) in relation and (c, b) in relation
                for c in elems
            )
            if not has_between:
                edges.append((a, b))
    return edges


def find_levels(elems, edges):
    below = {e: [] for e in elems}
    for a, b in edges:
        below[b].append(a)

    levels = {}

    def level_of(e):
        if e not in levels:
            if below[e]:
                levels[e] = 1 + max(level_of(x) for x in below[e])
            else:
                levels[e] = 0
        return levels[e]

    for e in elems:
        level_of(e)
    return levels


def draw_hasse(elems, edges, title):
    levels = find_levels(elems, edges)

    by_level = {}
    for e in elems:
        by_level.setdefault(levels[e], []).append(e)

    pos = {}
    for lvl, group in by_level.items():
        group.sort(key=label)
        n = len(group)
        for i, e in enumerate(group):
            pos[e] = (i - (n - 1) / 2, lvl)

    plt.figure(figsize=(8, 6))

    for a, b in edges:
        plt.plot(
            [pos[a][0], pos[b][0]],
            [pos[a][1], pos[b][1]],
            color="black",
            linewidth=1.5,
            zorder=1,
        )

    for e in elems:
        x, y = pos[e]
        plt.text(
            x,
            y,
            label(e),
            ha="center",
            va="center",
            fontsize=12,
            zorder=2,
            bbox=dict(boxstyle="circle,pad=0.5", fc="lightblue", ec="black"),
        )

    plt.title(title, fontsize=14)
    plt.axis("off")
    plt.margins(0.15)
    plt.tight_layout()
    plt.show()


def minimal_elements(elems, relation):
    return [
        a for a in elems
        if not any(b != a and (b, a) in relation for b in elems)
    ]


def maximal_elements(elems, relation):
    return [
        a for a in elems
        if not any(b != a and (a, b) in relation for b in elems)
    ]


def least_element(elems, relation):
    for a in elems:
        if all((a, b) in relation for b in elems):
            return a
    return None


def greatest_element(elems, relation):
    for a in elems:
        if all((b, a) in relation for b in elems):
            return a
    return None


def upper_bounds(elems, relation, subset):
    return [u for u in elems if all((x, u) in relation for x in subset)]


def lower_bounds(elems, relation, subset):
    return [l for l in elems if all((l, x) in relation for x in subset)]


def lub(elems, relation, subset):
    bounds = upper_bounds(elems, relation, subset)
    for u in bounds:
        if all((u, v) in relation for v in bounds):
            return u
    return None


def glb(elems, relation, subset):
    bounds = lower_bounds(elems, relation, subset)
    for l in bounds:
        if all((m, l) in relation for m in bounds):
            return l
    return None


def get_poset_from_user():
    print("\nChoose the type of POSET:")
    print("  1. Divisors of n under divisibility        (e.g. D30)")
    print("  2. Your own numbers under divisibility     (e.g. 1 2 3 4 6 12)")
    print("  3. Power set of a set under subset (⊆)     (e.g. {a, b, c})")
    print("  4. Custom elements and custom relation pairs")
    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        try:
            n = int(input("Enter n: "))
        except ValueError:
            print("Please enter a whole number.")
            return None
        if n < 1:
            print("n must be a positive integer.")
            return None
        elems = [d for d in range(1, n + 1) if n % d == 0]
        return elems, divisibility_relation(elems), f"Hasse Diagram of D{n} under divisibility"

    if choice == "2":
        try:
            elems = sorted(set(int(x) for x in input("Enter numbers (space separated): ").split()))
        except ValueError:
            print("Please enter whole numbers only.")
            return None
        if not elems or elems[0] < 1:
            print("Enter at least one number, and all must be positive.")
            return None
        return elems, divisibility_relation(elems), "Hasse Diagram under divisibility"

    if choice == "3":
        base = unique(convert(x) for x in input("Enter elements of the set (space separated): ").split())
        elems = power_set(base)
        return elems, subset_relation(elems), "Hasse Diagram of Power Set under ⊆"

    if choice == "4":
        elems = unique(convert(x) for x in input("Enter elements (space separated): ").split())
        if not elems:
            print("You need at least one element.")
            return None

        print("Enter relation pairs as  a,b  (meaning a <= b). One per line.")
        print("Press ENTER on an empty line when finished.")
        relation = set()
        while True:
            line = input("  pair: ").strip()
            if line == "":
                break
            try:
                a, b = line.split(",")
                a, b = convert(a.strip()), convert(b.strip())
            except ValueError:
                print("   Wrong format. Write like  1,2")
                continue
            if a not in elems or b not in elems:
                print("   Both elements must be from the set!")
                continue
            relation.add((a, b))

        auto = input("Add missing reflexive & transitive pairs automatically? (y/n): ").strip().lower()
        if auto == "y":
            relation = reflexive_transitive_closure(elems, relation)
        return elems, relation, "Hasse Diagram of the given relation"

    print("Invalid choice.")
    return None


def get_subset_from_user(elems):
    name_to_elem = {label(e): e for e in elems}
    print("\nType the subset elements separated by spaces.")
    print("Available elements:", "  ".join(label(e) for e in elems))
    tokens = input("Subset: ").split()

    if not tokens:
        print("   Subset cannot be empty.")
        return None

    subset = []
    for token in tokens:
        if token not in name_to_elem:
            print(f"   '{token}' is not in the set. Try again.")
            return None
        subset.append(name_to_elem[token])
    return unique(subset)


def print_poset_check(elems, relation):
    reflexive, antisymmetric, transitive = check_poset(elems, relation)
    print("\n--- POSET CHECK ---")
    print("Reflexive     :", "Yes" if reflexive else "No")
    print("Antisymmetric :", "Yes" if antisymmetric else "No")
    print("Transitive    :", "Yes" if transitive else "No")
    is_poset = reflexive and antisymmetric and transitive
    print("Result        :", "It IS a POSET." if is_poset else "It is NOT a POSET.")
    return is_poset


def print_basic_properties(elems, relation, edges):
    print("\n--- RELATION ---")
    print("Pairs in R (a <= b):", len(relation))

    print("\n--- HASSE DIAGRAM EDGES (covering pairs) ---")
    if edges:
        print(", ".join(f"({label(a)}, {label(b)})" for a, b in edges))
    else:
        print("None (no two elements are comparable)")

    print("\n--- SPECIAL ELEMENTS ---")
    print("Minimal elements  :", show_list(minimal_elements(elems, relation)))
    print("Maximal elements  :", show_list(maximal_elements(elems, relation)))

    least = least_element(elems, relation)
    greatest = greatest_element(elems, relation)
    print("Least element     :", label(least) if least is not None else "Does not exist")
    print("Greatest element  :", label(greatest) if greatest is not None else "Does not exist")


def print_bounds(elems, relation, subset):
    print("\n--- BOUNDS OF THE SUBSET", show_list(subset), "---")
    supremum = lub(elems, relation, subset)
    infimum = glb(elems, relation, subset)

    print("Upper bounds  :", show_list(upper_bounds(elems, relation, subset)))
    print("Lower bounds  :", show_list(lower_bounds(elems, relation, subset)))
    print("LUB (supremum):", label(supremum) if supremum is not None else "Does not exist")
    print("GLB (infimum) :", label(infimum) if infimum is not None else "Does not exist")


def main():
    print("=" * 50)
    print("     HASSE DIAGRAM & POSET ANALYZER")
    print("=" * 50)

    while True:
        data = get_poset_from_user()
        if data is None:
            continue
        elems, relation, title = data

        if not print_poset_check(elems, relation):
            print("\nA Hasse diagram can only be drawn for a POSET.")
            print("Tip: in option 4, say 'y' to auto-add reflexive/transitive pairs.")
        else:
            edges = covering_pairs(elems, relation)
            print_basic_properties(elems, relation, edges)

            while True:
                answer = input("\nFind bounds / LUB / GLB of a subset? (y/n): ").strip().lower()
                if answer != "y":
                    break
                subset = get_subset_from_user(elems)
                if subset is not None:
                    print_bounds(elems, relation, subset)

            print("\nDrawing Hasse diagram... (close the window to continue)")
            draw_hasse(elems, edges, title)

        again = input("\nAnalyze another POSET? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
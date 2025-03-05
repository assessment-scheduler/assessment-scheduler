from ortools.sat.python import cp_model


def week_day_to_k(week, day):
    return (week - 1) * 7 + day


def build_stage1_model(courses, c, K, M):
    model = cp_model.CpModel()
    x = {}
    # Create x variables for Stage 1
    for i, course in enumerate(courses):
        for j_idx, assessment in enumerate(course['assessments']):
            start_k = week_day_to_k(assessment['start_week'], assessment['start_day'])
            end_k = week_day_to_k(assessment['end_week'], assessment['end_day'])
            for k in range(start_k, end_k + 1):
                if 1 <= k <= K:
                    x[(k, i, j_idx)] = model.NewBoolVar(f'x1_{k}_{i}_{j_idx}')
    # Each assessment scheduled exactly once
    for i, course in enumerate(courses):
        for j_idx, assessment in enumerate(course['assessments']):
            start_k = week_day_to_k(assessment['start_week'], assessment['start_day'])
            end_k = week_day_to_k(assessment['end_week'], assessment['end_day'])
            possible_ks = [k for k in range(start_k, end_k + 1) if 1 <= k <= K]
            model.AddExactlyOne([x[(k, i, j_idx)] for k in possible_ks])
    # Proctored assessments only on weekdays
    for (k, i, j_idx), var in x.items():
        assessment = courses[i]['assessments'][j_idx]
        if assessment['proctored']:
            day_of_week = (k - 1) % 7 + 1
            if day_of_week > 5:
                model.Add(var == 0)
    # Each course and time has at most one assessment
    course_time_vars = {}
    for (k, i, j_idx), var in x.items():
        key = (k, i)
        course_time_vars.setdefault(key, []).append(var)
    for key, vars_list in course_time_vars.items():
        model.Add(sum(vars_list) <= 1)
    # Define U as the maximum load
    U = model.NewIntVar(0, 10000000, 'U')
    # Weight matrix from assessments' percentages
    w = [[a['percentage'] for a in course['assessments']] for course in courses]
    # Ensure load does not exceed U on any day for each course combination
    for k in range(1, K + 1):
        for i in range(len(courses)):
            terms = []
            for i_prime in range(len(courses)):
                for j_idx in range(len(courses[i_prime]['assessments'])):
                    x_key = (k, i_prime, j_idx)
                    if x_key in x:
                        coeff = c[i][i_prime] * w[i_prime][j_idx]
                        terms.append(x[x_key] * coeff)
            if terms:
                model.Add(sum(terms) <= U)
    # Minimize U
    model.Minimize(U)
    return model, x, U


def solve_stage1(courses, c, K, M):
    model, x, U = build_stage1_model(courses, c, K, M)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL:
        U_star = solver.Value(U)
        print(f"Stage 1 solved with U* = {U_star}")
        return U_star, solver, x
    else:
        print("Stage 1 failed to find an optimal solution.")
        exit()


def build_stage2_model(courses, c, phi, U_star, K, d, M):
    model = cp_model.CpModel()
    x = {}
    # Create x variables for Stage 2
    for i, course in enumerate(courses):
        for j_idx, assessment in enumerate(course['assessments']):
            start_k = week_day_to_k(assessment['start_week'], assessment['start_day'])
            end_k = week_day_to_k(assessment['end_week'], assessment['end_day'])
            for k in range(start_k, end_k + 1):
                if 1 <= k <= K:
                    x[(k, i, j_idx)] = model.NewBoolVar(f'x2_{k}_{i}_{j_idx}')
    # Each assessment scheduled exactly once
    for i, course in enumerate(courses):
        for j_idx, assessment in enumerate(course['assessments']):
            start_k = week_day_to_k(assessment['start_week'], assessment['start_day'])
            end_k = week_day_to_k(assessment['end_week'], assessment['end_day'])
            possible_ks = [k for k in range(start_k, end_k + 1) if 1 <= k <= K]
            model.AddExactlyOne([x[(k, i, j_idx)] for k in possible_ks])
    # Proctored assessments only on weekdays
    for (k, i, j_idx), var in x.items():
        assessment = courses[i]['assessments'][j_idx]
        if assessment['proctored']:
            day_of_week = (k - 1) % 7 + 1
            if day_of_week > 5:
                model.Add(var == 0)
    # Each course and time has at most one assessment
    course_time_vars = {}
    for (k, i, j_idx), var in x.items():
        key = (k, i)
        course_time_vars.setdefault(key, []).append(var)
    for key, vars_list in course_time_vars.items():
        model.Add(sum(vars_list) <= 1)
    # Ensure load does not exceed U*
    w = [[a['percentage'] for a in course['assessments']] for course in courses]
    for k in range(1, K + 1):
        for i in range(len(courses)):
            terms = []
            for i_prime in range(len(courses)):
                for j_idx in range(len(courses[i_prime]['assessments'])):
                    x_key = (k, i_prime, j_idx)
                    if x_key in x:
                        coeff = c[i][i_prime] * w[i_prime][j_idx]
                        terms.append(x[x_key] * coeff)
            if terms:
                model.Add(sum(terms) <= U_star)
    # Enforce spacing between overlapping courses
    for i in range(len(courses)):
        for i_prime in range(len(courses)):
            if i >= i_prime or phi[i][i_prime] == 0:
                continue  # Skip duplicates and non-overlapping courses
            for j_idx in range(len(courses[i]['assessments'])):
                for j_prime_idx in range(len(courses[i_prime]['assessments'])):
                    for k in range(1, K - d + 1):
                        var1 = x.get((k, i, j_idx), None)
                        var2 = x.get((k + d + 1, i_prime, j_prime_idx), None)
                        if var1 is not None and var2 is not None:
                            model.Add(var1 + var2 <= 1)
    # Create y variables for time windows
    y = {k: model.NewBoolVar(f'y_{k}') for k in range(1, K - d + 1)}
    # Add window constraints for y variables
    for k in range(1, K - d + 1):
        window_assessments = []
        for k_prime in range(k, k + d + 1):
            if k_prime > K:
                continue
            for i_prime in range(len(courses)):
                for j_idx in range(len(courses[i_prime]['assessments'])):
                    x_key = (k_prime, i_prime, j_idx)
                    if x_key in x:
                        window_assessments.append(x[x_key])
        model.Add(sum(window_assessments) <= 1).OnlyEnforceIf(y[k])
        model.Add(sum(window_assessments) >= 2).OnlyEnforceIf(y[k].Not())
    # Maximize Y*
    model.Maximize(sum(y[k] for k in range(1, K - d + 1)))
    return model, x, y


def solve_stage2(courses, c, phi, U_star, K, d, M):
    model, x, y = build_stage2_model(courses, c, phi, U_star, K, d, M)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60  # Adjust if needed
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL:
        Y_star = sum(solver.Value(y[k]) for k in range(1, K - d + 1))
        probability = Y_star / (K - d)
        print(f"\nStage 2 solved with Y* = {Y_star}")
        print(f"Probability: {probability:.3f}")
        schedule = []
        for (k, i, j_idx), var in x.items():
            if solver.Value(var):
                assessment = courses[i]['assessments'][j_idx]
                week = (k - 1) // 7 + 1
                day_of_week = (k - 1) % 7 + 1
                course_name = courses[i]['code']
                assessment_name = f"{assessment['name']}-({assessment['percentage']})"
                schedule.append((k, week, day_of_week, course_name, assessment_name))
        schedule.sort(key=lambda x: x[0])
        return schedule, Y_star, probability
    else:
        print("Stage 2 failed to find an optimal solution.")
        exit()


def print_schedule(schedule, U_star, d, probability):
    print(f"\nStage 2 Schedule:")
    print(f"U* = {U_star}, d = {d}, Y*/K-d = {probability:.3f}")
    print("-" * 55)
    print(f"| {'K':<2} | {'WK':<3} | {'DAY':<4} | {'Assessment':<35} |")
    print("-" * 55)
    for entry in schedule:
        k, week, day, course, assessment = entry
        print(f"| {k:<2} | {week:<3} | {day:<4} | {course}-{assessment:<30} |")
    print("-" * 55)
    
"""
def main():
    # Data
    courses = [
        {  # C1601 (index 0)
            'code': 'C1601',
            'assessments': [
                {'name': 'A1', 'percentage': 5, 'start_week': 3, 'start_day': 1,
                 'end_week': 4, 'end_day': 7, 'proctored': 0},
                {'name': 'A2', 'percentage': 6, 'start_week': 7, 'start_day': 1,
                 'end_week': 8, 'end_day': 7, 'proctored': 0},
                {'name': 'A3', 'percentage': 6, 'start_week': 10, 'start_day': 1,
                 'end_week': 11, 'end_day': 7, 'proctored': 0},
                {'name': 'CW1', 'percentage': 10, 'start_week': 8, 'start_day': 1,
                 'end_week': 9, 'end_day': 7, 'proctored': 1},
                {'name': 'CW2', 'percentage': 20, 'start_week': 12, 'start_day': 1,
                 'end_week': 12, 'end_day': 7, 'proctored': 1},
            ]
        },
        {  # C1602 (index 1)
            'code': 'C1602',
            'assessments': [
                {'name': 'A1', 'percentage': 5, 'start_week': 3, 'start_day': 1,
                 'end_week': 4, 'end_day': 7, 'proctored': 0},
                {'name': 'A2', 'percentage': 6, 'start_week': 8, 'start_day': 1,
                 'end_week': 9, 'end_day': 7, 'proctored': 0},
                {'name': 'A3', 'percentage': 6, 'start_week': 10, 'start_day': 1,
                 'end_week': 11, 'end_day': 7, 'proctored': 0},
                {'name': 'CW1', 'percentage': 10, 'start_week': 6, 'start_day': 1,
                 'end_week': 7, 'end_day': 7, 'proctored': 1},
                {'name': 'CW2', 'percentage': 20, 'start_week': 12, 'start_day': 1,
                 'end_week': 12, 'end_day': 7, 'proctored': 1},
            ]
        },
        {  # C1603 (index 2)
            'code': 'C1603',
            'assessments': [
                {'name': 'A1', 'percentage': 6, 'start_week': 3, 'start_day': 1,
                 'end_week': 4, 'end_day': 7, 'proctored': 0},
                {'name': 'A2', 'percentage': 7, 'start_week': 6, 'start_day': 1,
                 'end_week': 7, 'end_day': 7, 'proctored': 0},
                {'name': 'A3', 'percentage': 7, 'start_week': 10, 'start_day': 1,
                 'end_week': 11, 'end_day': 7, 'proctored': 0},
                {'name': 'CW1', 'percentage': 10, 'start_week': 8, 'start_day': 1,
                 'end_week': 9, 'end_day': 7, 'proctored': 1},
                {'name': 'CW2', 'percentage': 20, 'start_week': 12, 'start_day': 1,
                 'end_week': 12, 'end_day': 7, 'proctored': 1},
            ]
        }
    ]

    # Class sizes matrix
    c = [
        [450, 100, 0],
        [100, 350, 150],
        [0, 150, 300]
    ]
    # Phi matrix (1 if at least one student is registered for both courses)
    phi = [[1 if ci > 0 else 0 for ci in row] for row in c]

    K = 84  # 12 weeks * 7 days
    d = 3   # Minimum spacing between overlapping courses
    M = 1000  # A large value for constraints

    U_star, _, _ = solve_stage1(courses, c, K, M)
    schedule, Y_star, probability = solve_stage2(courses, c, phi, U_star, K, d, M)
    print_schedule(schedule, U_star, d, probability)


if __name__ == '__main__':
    main()
    
"""
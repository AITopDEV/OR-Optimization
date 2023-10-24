from ortools.sat.python import cp_model

model = cp_model.CpModel()

people = ["James", "Daniel", "Emily", "Sophie"]
starters = ["Carpaccio", "Onion Soup", "Mushroom Tart", "Prawn Cocktail"]
main_courses = ["Vegan Pie", "Filet Steak", "Baked Mackerel", "Fried Chicken"]
deserts = ["Ice Cream", "Chocolate Cake", "Apple Crumble", "Tiramisu"]
drinks = ["Beer", "Coke", "Red Wine", "White Wine"]

starter_vars = {p: {s: model.NewBoolVar('') for s in starters} for p in people}
main_courses_vars = {p: {m: model.NewBoolVar('') for m in main_courses} for p in people}
deserts_vars = {p: {d: model.NewBoolVar('') for d in deserts} for p in people}
drinks_vars = {p: {dr: model.NewBoolVar('') for dr in drinks} for p in people}

# The carpacciso starter is not combined with the vegan pie as main course and the filet steak main course is not followed by ice cream as desert
for p in people:
    model.AddImplication(
        starter_vars[p]['Carpaccio'], main_courses_vars[p]['Vegan Pie'].Not())
    model.AddImplication(
        main_courses_vars[p]['Filet Steak'], deserts_vars[p]['Ice Cream'].Not())
    
# Emily does not have prawn cocktail or onion soup as starter and none of the men has beer or coke to drink.
model.Add(starter_vars['Emily']['Prawn Cocktail'] == 0)
model.Add(starter_vars['Emily']['Onion Soup'] == 0)

for p in ["James", "Daniel"]:
    model.Add(drinks_vars[p]['Beer'] == 0)
    model.Add(drinks_vars[p]['Coke'] == 0)

# The person having prawn cocktail as starter has baked mackerel as main course and the filet steak main course works well with the red wine.
for p in people:
    model.AddImplication(
        starter_vars[p]['Prawn Cocktail'], main_courses_vars[p]['Baked Mackerel'])
    model.AddImplication(
        main_courses_vars[p]['Filet Steak'], drinks_vars[p]['Red Wine'])

# One of the men has white wine as drink and one of the women drinks coke.
model.Add(sum(drinks_vars[man]['White Wine']
          for man in ["James", "Daniel"]) == 1)
model.Add(sum(drinks_vars[woman]['Coke']
          for woman in ["Emily", "Sophie"]) == 1)

# The vegan pie main always comes with mushroom tart as starter and vice versa; also, the onion soup and filet steak are always served together.
for p in people:
    model.AddImplication(
        main_courses_vars[p]['Vegan Pie'], starter_vars[p]['Mushroom Tart'])
    model.AddImplication(
        starter_vars[p]['Mushroom Tart'], main_courses_vars[p]['Vegan Pie'])

    model.AddImplication(
        starter_vars[p]['Onion Soup'], main_courses_vars[p]['Filet Steak'])
    model.AddImplication(
        main_courses_vars[p]['Filet Steak'], starter_vars[p]['Onion Soup'])

# Emily orders beer as drink or has fried chicken as main and ice cream as desert,; James orders cocke as drink or has onion soup as stater and filet steak as main.

emily_helper_var = model.NewBoolVar('Emily helper')
james_helper_var = model.NewBoolVar('James helper')

model.AddBoolAnd([main_courses_vars['Emily']['Fried Chicken'], deserts_vars['Emily']['Ice Cream']]).OnlyEnforceIf(emily_helper_var)
model.AddBoolAnd([starter_vars['James']['Onion Soup'], main_courses_vars['James']['Filet Steak']]).OnlyEnforceIf(james_helper_var)

model.AddBoolOr([drinks_vars['Emily']['Beer'], emily_helper_var])
model.AddBoolOr([drinks_vars['James']['Coke'], james_helper_var])


# Sophie orders chocolate cake but does not drink beer nor likes fried chicken; Daniel orders apple crumble for dessert but has neither carpaccio nor mushroom tart as starter.
model.Add(deserts_vars['Sophie']['Chocolate Cake'] == 1)
model.Add(drinks_vars['Sophie']['Beer'] == 0)
model.Add(main_courses_vars['Sophie']['Fried Chicken'] == 0)

model.Add(deserts_vars['Daniel']['Apple Crumble'] == 1)
model.Add(starter_vars['Daniel']['Carpaccio'] == 0)
model.Add(starter_vars['Daniel']['Mushroom Tart'] == 0)

# Implicit: For each person, he/she must order exactly one starter, main course, desert and drink
for p in people:
    model.Add(sum(starter_vars[p].values()) == 1)
    model.Add(sum(main_courses_vars[p].values()) == 1)
    model.Add(sum(deserts_vars[p].values()) == 1)
    model.Add(sum(drinks_vars[p].values()) == 1)

# As many different things
total_variety = sum(sum(choice[list(choice.keys())[0]].values()) for choice in [starter_vars, main_courses_vars, deserts_vars, drinks_vars])
model.Maximize(total_variety)

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    for p in people:
        print(f'{p} orders:')
        for type_vars in [starter_vars, main_courses_vars, deserts_vars, drinks_vars]:
            print('\t', end='')
            for dish, var in type_vars[p].items():
                if solver.Value(var):
                    print(dish, end=' ')
            print()

else:
    print('no Solution')

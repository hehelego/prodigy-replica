#/usr/bin/fish

function check
    echo checking $argv[1]
    set p "examples/equivalence/$argv[1]"
    set q "examples/equivalence/$argv[2]"
    echo $q | python main.py $p $q
end

check geometric_shifted.pgcl geometric_shifted_invariant.pgcl
exit

check dep_bern.pgcl dep_bern_invariant.pgcl
check endless_conditioning.pgcl endless_conditioning_invariant.pgcl
check dueling_cowboys_parameter.pgcl dueling_cowboys_parameter_invariant.pgcl

check geometric.pgcl geometric_invariant.pgcl check geometric_observe.pgcl geometric_observe_invariant.pgcl check geometric_observe_parameter.pgcl geometric_observe_parameter_invariant.pgcl
check geometric_parameter.pgcl geometric_parameter_invariant.pgcl
check geometric_shifted.pgcl geometric_shifted_invariant.pgcl


check ky_die.pgcl ky_die_invariant.pgcl
check ky_die_2.pgcl ky_die_2_invariant.pgcl
check ky_die_parameter.pgcl ky_die_parameter_invariant.pgcl

check n_geometric.pgcl n_geometric_invariant.pgcl

check negative_binomial_parameter.pgcl negative_binomial_parameter_invariant.pgcl

check random_walk.pgcl random_walk_invariant.pgcl

check running_paper_example.pgcl running_paper_example_invariant.pgcl

check trivial_iid.pgcl trivial_iid_invariant.pgcl

# test scalability
echo "Scalability benchmarking:"
for i in (seq 10)
    echo "
    nat x;

    x := geometric(1/2);
    loop($i){
    if(x > 15) { {x := x+1}[1/2]{x := x-1} }
    else { skip }
    }" >scale.pgcl
    echo "loop $i iterations"
    time python main.py scale.pgcl scale.pgcl >/dev/null 2>/dev/null
end

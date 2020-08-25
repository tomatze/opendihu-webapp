#!/usr/bin/python3

import unittest

import cpp_structure

class TestParser(unittest.TestCase):

    example_root = "../opendihu-clean/examples/"
    example_paths = [
        "diffusion/anisotropic_diffusion/src/anisotropic_diffusion2d.cpp",
        "diffusion/anisotropic_diffusion/src/anisotropic_diffusion3d.cpp",
        "diffusion/diffusion1d/src/diffusion_1d.cpp",
        # IGNORE because of surrounding if-statements
        #"diffusion/diffusion1d/src/diffusion_1d_pod.cpp",
        "diffusion/diffusion2d/src/diffusion_2d_1st_order.cpp",
        "diffusion/diffusion2d/src/diffusion_2d_2nd_order.cpp",
        "diffusion/diffusion3d/src/diffusion.cpp",
        "diffusion/reaction_diffusion2d/src/diffusion_2d_1st_order.cpp",
        "diffusion/reaction_diffusion2d/src/reaction_diffusion_2d.cpp",
        "electrophysiology/cellml/cellml_on_gpu/multiple_instances/src/cellml.cpp",
        "electrophysiology/cellml/cellml_on_gpu/single_instance/src/cellml.cpp",
        "electrophysiology/cellml/hodgkin-huxley_shorten_ocallaghan_davidson_soboleva_2007/src/cellml.cpp",
        "electrophysiology/cellml/shorten/src/cellml.cpp",
        "electrophysiology/fibers/cuboid/src/cuboid.cpp",
        "electrophysiology/fibers/fibers_contraction/no_precice/src/biceps_contraction.cpp",
        # IGNORE Dummy
        #"electrophysiology/fibers/fibers_contraction/no_precice/src/biceps_contraction_no_cell.cpp",
        "electrophysiology/fibers/fibers_contraction/no_precice/src/biceps_contraction_not_fast.cpp",
        "electrophysiology/fibers/fibers_contraction/with_precice/src/contraction.cpp",
        "electrophysiology/fibers/fibers_contraction/with_precice/src/fibers.cpp",
        # IGNORE Dummy
        #"electrophysiology/fibers/fibers_contraction/with_tendons_precice/src/muscle_precice.cpp",
        "electrophysiology/fibers/fibers_contraction/with_tendons_precice/src/tendon.cpp",
        "electrophysiology/fibers/fibers_contraction/with_tendons_precice/src/tendon_precice.cpp",
        "electrophysiology/fibers/fibers_emg/src/fast_fibers_emg.cpp",
        "electrophysiology/fibers/fibers_emg/src/fast_fibers_shorten_emg.cpp",
        "electrophysiology/fibers/fibers_emg/src/fibers_emg.cpp",
        "electrophysiology/fibers/fibers_emg/src/fibers_emg_2d_output.cpp",
        "electrophysiology/fibers/fibers_emg/src/fibers_febio.cpp",
        "electrophysiology/fibers/fibers_emg/src/fibers_linear_elasticity.cpp",
        "electrophysiology/fibers/fibers_fat_emg/failed/src/static_biceps_emg.cpp",
        "electrophysiology/fibers/fibers_fat_emg/src/static_biceps_emg.cpp",
        "electrophysiology/fibers/load_balancing/src/multiple_fibers.cpp",
        "electrophysiology/fibers/load_balancing/src/repartitioning.cpp",
        "electrophysiology/fibers/load_balancing/src/with_load_balancing.cpp",
        "electrophysiology/fibers/multiple_fibers/src/multiple_fibers.cpp",
        "electrophysiology/fibers/multiple_fibers_cubes_partitioning/src/multiple_fast_fibers_57_states.cpp",
        "electrophysiology/fibers/multiple_fibers_cubes_partitioning/src/multiple_fibers.cpp",
        "electrophysiology/fibers/multiple_fibers_cubes_partitioning/src/multiple_fibers_57_states.cpp",
        "electrophysiology/monodomain/hodgkin-huxley_shorten_ocallaghan_davidson_soboleva_2007/src/fast_monodomain.cpp",
        "electrophysiology/monodomain/hodgkin-huxley_shorten_ocallaghan_davidson_soboleva_2007/src/monodomain.cpp",
        "electrophysiology/monodomain/hodgkin_huxley/src/hodgkin_huxley_explicit.cpp",
        "electrophysiology/monodomain/hodgkin_huxley/src/hodgkin_huxley_godunov.cpp",
        "electrophysiology/monodomain/hodgkin_huxley/src/hodgkin_huxley_strang.cpp",
        "electrophysiology/monodomain/hodgkin_huxley-razumova/src/monodomain.cpp",
        "electrophysiology/monodomain/hodgkin_huxley_fast/src/fast_fiber.cpp",
        "electrophysiology/monodomain/hodgkin_huxley_fast/src/not_fast_fiber.cpp",
        "electrophysiology/monodomain/motoneuron_cisi_kohn/src/motoneuron_cisi_kohn.cpp",
        "electrophysiology/monodomain/motoneuron_hodgkin_huxley/src/motoneuron_hodgkin_huxley.cpp",
        "electrophysiology/monodomain/new_slow_TK_2014_12_08/src/shorten_explicit.cpp",
        "electrophysiology/monodomain/new_slow_TK_2014_12_08/src/shorten_implicit.cpp",
        "electrophysiology/monodomain/new_slow_TK_2014_12_08/src/shorten_pod.cpp",
        "electrophysiology/monodomain/pod/src/hodgkin_huxley_explicit.cpp",
        "electrophysiology/monodomain/pod/src/hodgkin_huxley_godunov.cpp",
        "electrophysiology/monodomain/pod/src/hodgkin_huxley_pod.cpp",
        "electrophysiology/monodomain/pod/src/hodgkin_huxley_strang.cpp",
        "electrophysiology/monodomain/shorten_ocallaghan_davidson_soboleva_2007/src/shorten_explicit.cpp",
        "electrophysiology/monodomain/shorten_ocallaghan_davidson_soboleva_2007/src/shorten_implicit.cpp",
        "electrophysiology/multidomain/multidomain_contraction/src/multidomain_contraction.cpp",
        "electrophysiology/multidomain/multidomain_contraction/src/multidomain_contraction_hodgkin_huxley_razumova.cpp",
        "electrophysiology/multidomain/multidomain_contraction/src/multidomain_contraction_without_fat.cpp",
        "electrophysiology/multidomain/multidomain_motoneuron/src/multidomain_neuromuscular.cpp",
        "electrophysiology/multidomain/multidomain_no_fat/src/multidomain.cpp",
        "electrophysiology/multidomain/multidomain_no_fat/src/multidomain_output.cpp",
        "electrophysiology/multidomain/multidomain_with_fat/src/multidomain_shorten_with_fat.cpp",
        "electrophysiology/multidomain/multidomain_with_fat/src/multidomain_with_fat.cpp",
        # IGNORE TODO using insted of define
        #"electrophysiology/neuromuscular/neurons_with_contraction/src/neurons_with_contraction.cpp",
        #"electrophysiology/neuromuscular/only_neurons/src/only_neurons.cpp",
        # TODO problem.fixInvalidFibersInFile();
        "fiber_tracing/parallel_fiber_estimation/src/fix.cpp",
        "fiber_tracing/parallel_fiber_estimation/src/generate.cpp",
        "fiber_tracing/parallel_fiber_estimation/src/generate_quadratic.cpp",
        "fiber_tracing/parallel_fiber_estimation/src/refine.cpp",
        "fiber_tracing/streamline_tracer/src/laplace_structured_hermite.cpp",
        "fiber_tracing/streamline_tracer/src/laplace_structured_linear.cpp",
        "fiber_tracing/streamline_tracer/src/laplace_structured_quadratic.cpp",
        "fiber_tracing/streamline_tracer/src/laplace_unstructured_hermite.cpp",
        "fiber_tracing/streamline_tracer/src/laplace_unstructured_linear.cpp",
        "fiber_tracing/streamline_tracer/src/laplace_unstructured_quadratic.cpp",
        "laplace/laplace1d/src/laplace_hermite.cpp",
        "laplace/laplace1d/src/laplace_linear.cpp",
        "laplace/laplace1d/src/laplace_quadratic.cpp",
        "laplace/laplace2d/src/laplace_hermite.cpp",
        "laplace/laplace2d/src/laplace_regular.cpp",
        "laplace/laplace2d/src/laplace_structured.cpp",
        "laplace/laplace2d/src/laplace_unstructured.cpp",
        "laplace/laplace3d/src/laplace_hermite.cpp",
        "laplace/laplace3d/src/laplace_regular_fixed.cpp",
        "laplace/laplace3d/src/laplace_structured_deformable.cpp",
        "laplace/laplace3d/src/laplace_unstructured.cpp",
        # IGNORE
        #"laplace/laplace3d/src/petsc_test.cpp",
        "laplace/laplace3d_surface/src/laplace_surface.cpp",
        "laplace/laplace_composite/src/laplace_composite_2d.cpp",
        "laplace/laplace_composite/src/laplace_composite_3d.cpp",
        "laplace/laplace_composite/src/laplace_composite_linear_2d.cpp",
        "laplace/laplace_composite/src/laplace_composite_linear_3d.cpp",
        "poisson/poisson1d/poisson_example_1d.cpp",
        "poisson/poisson2d/poisson_example_2d.cpp",
        "solid_mechanics/chaste/src/3d_muscle.cpp",
        # IGNORE
        #"solid_mechanics/chaste/src/solving_elasticity_problems_tutorial.cpp",
        "solid_mechanics/dynamic_mooney_rivlin/gelatine1/src/dynamic.cpp",
        "solid_mechanics/dynamic_mooney_rivlin/gelatine2/src/dynamic.cpp",
        "solid_mechanics/dynamic_mooney_rivlin/muscle/src/dynamic_transversely_isotropic.cpp",
        "solid_mechanics/dynamic_mooney_rivlin/muscle_with_fat/src/muscle_with_fat.cpp",
        "solid_mechanics/dynamic_mooney_rivlin/rod/src/dynamic_isotropic.cpp",
        "solid_mechanics/dynamic_mooney_rivlin/rod/src/dynamic_transversely_isotropic.cpp",
        "solid_mechanics/dynamic_mooney_rivlin/tendon/src/tendon.cpp",
        "solid_mechanics/linear_elasticity/box/src/linear_elasticity_2d.cpp",
        "solid_mechanics/linear_elasticity/box/src/linear_elasticity_3d.cpp",
        "solid_mechanics/linear_elasticity/with_3d_activation/src/lin_elasticity_with_3d_activation_linear.cpp",
        "solid_mechanics/linear_elasticity/with_3d_activation/src/lin_elasticity_with_3d_activation_quadratic.cpp",
        "solid_mechanics/linear_elasticity/with_fiber_activation/src/lin_elasticity_with_fibers.cpp",
        "solid_mechanics/mooney_rivlin_febio/src/febio.cpp",
        "solid_mechanics/mooney_rivlin_febio/src/opendihu.cpp",
        "solid_mechanics/mooney_rivlin_isotropic/src/3d_hyperelasticity.cpp",
        "solid_mechanics/mooney_rivlin_transiso/src/3d_hyperelasticity.cpp",
        # IGNORE because of Material
        #"solid_mechanics/shear_test/src/compressible_mooney_rivlin.cpp",
        #"solid_mechanics/shear_test/src/compressible_mooney_rivlin_decoupled.cpp",
        #"solid_mechanics/shear_test/src/incompressible_mooney_rivlin.cpp",
        "solid_mechanics/shear_test/src/linear.cpp",
        # IGNORE because of Material
        #"solid_mechanics/shear_test/src/nearly_incompressible_mooney_rivlin.cpp",
        #"solid_mechanics/shear_test/src/nearly_incompressible_mooney_rivlin_decoupled.cpp",
        "solid_mechanics/shear_test/src/nearly_incompressible_mooney_rivlin_febio.cpp",
        # IGNORE because of Material
        #"solid_mechanics/tensile_test/src/compressible_mooney_rivlin.cpp",
        #"solid_mechanics/tensile_test/src/compressible_mooney_rivlin_decoupled.cpp",
        #"solid_mechanics/tensile_test/src/incompressible_mooney_rivlin.cpp",
        "solid_mechanics/tensile_test/src/linear.cpp",
        # IGNORE because of Material
        #"solid_mechanics/tensile_test/src/nearly_incompressible_mooney_rivlin.cpp",
        #"solid_mechanics/tensile_test/src/nearly_incompressible_mooney_rivlin_decoupled.cpp",
        "solid_mechanics/tensile_test/src/nearly_incompressible_mooney_rivlin_febio.cpp"
    ]
    for i in range(len(example_paths)):
        example_paths[i] = example_root + example_paths[i]

    # this test parses all cpp examples and validates them
    def test_parse_and_validate_examples(self):
        example = cpp_structure.CPPTree()
        for path in self.example_paths:
            file = open(path, "r")
            src = file.read()
            file.close()
            example.parse_cpp_src(src)
            self.assertEqual(example.validate_cpp_src(), True, msg=path)

    # this test parses all examples (src1) and creates their src (src2)
    # it then parses src2 and compares the trees of both examples
    # if this fails, there is probably something wrong in Node.create_src()
    def test_create_src(self):
        example1 = cpp_structure.CPPTree()
        example2 = cpp_structure.CPPTree()
        for path in self.example_paths:
            file = open(path, "r")
            src1 = file.read()
            file.close()
            example1.parse_cpp_src(src1)
            src2 = str(example1)
            example2.parse_cpp_src(src2)
            self.assertEqual(example1.root.childs[0].compare(example2.root.childs[0]), True, msg=path)

if __name__ == '__main__':
    unittest.main()
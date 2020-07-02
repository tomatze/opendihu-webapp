# each dict entry corresponds to a cpp-template
# each template-dict can have a ordered list with template_arguments (assuming there are no template_arguments if omitted)

# possible outer templates (runnables) have the key runnable set to True (assuming False if ommited)

# templates that are discretizable in time have discretizableInTime set to True (assuming False if omited)
# "discretizableInTime" in template_arguments will get expanded to all classes, which have discretizableInTime == True

# templates that are a "TimeSteppingScheme" (e.g. all TimeSteppingScheme:: and OperatorSplitting::) have timeSteppingScheme set to True (assuming False if omited)
# "timeSteppingScheme" in template_arguments will get expanded to all classes, which have timeSteppingScheme == True

# templates with optional template_arguments can have the key template_arguments_needed set to the minimal required argument count
# template_arguments_needed is assumed to be len(template_arguments) if template_arguments_needed is omitted
# e.g. in BasisFunction::LagrangeOfOrder and PrescribedValues

# the keyword "Integer" can be used in template_arguments where an integer is expected (e.g. in CellmlAdapter)

# lists of the form [ "Mesh::" ] get auto expanded to [ "Mesh::StructuredRegularFixedOfDimension", "Mesh::Str..", ... ]

# templates added so far:
# TODO add postprocessing
# FastMonodomainSolver
# MuscleContractionSolver
# TODO add other specalized_solvers
# e.g. SpatialDiscretization::HyperelasticitySolver in solid_mechanics/shear_test/src/compressible_mooney_rivlin.cpp
# Control::MultipleInstances
# Control::Coupling
# Control::MapDofs
# OperatorSplitting::
# CellmlAdapter
# FunctionSpace::
# OutputWriter::OutputSurface
# TODO add other OutputWriters
# TimeSteppingScheme::
# TimeSteppingScheme::StaticBidomainSolver
# TimeSteppingScheme::MultidomainSolver
# TimeSteppingScheme::MultidomainWithFatSolver
# SpatialDiscretization::FiniteElementMethod
# Mesh::
# BasisFunction::
# Quadrature::
# Equation::
possible_solver_combinations = {
    "global" : {
        "python_options" : {
            "scenarioName" : {
                "description" : "name of the scenario",
                "type" : [ "string" ],
                "default" : "test-scenario"
            },
            "logFormat" : {
                "description" : "output-format of logfiles",
                "type" : [ "csv", "json" ],
                "default" : "csv"
            },
            "solverStructureDiagramFile" : {
                "description" : "filename of solver structure diagram",
                "type" : [ "string" ],
                "default" : "solver_structure.txt"
            }
            #TODO add meta
        }
    },


    "FastMonodomainSolver" : {
        # TODO is this runnable?
        "runnable" : True,
        #TODO can this be handled like a timeSteppingScheme?
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "Control::MultipleInstances" ]
        ]
    },
    "MuscleContractionSolver" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            # TODO this should only accept Mesh::StructuredDeformableOfDimension<3>
            # and maybe Mesh::CompositeOfDimension<3>?
            [ "Mesh::" ]
        ]
    },


    "Control::MultipleInstances" : {
        "runnable" : True,
        #TODO can this be handled like a timeSteppingScheme?
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "timeSteppingScheme" ]
        ]
    },
    "Control::Coupling" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "timeSteppingScheme" ],
            [ "timeSteppingScheme" ]
        ]
    },
    "Control::MapDofs" : {
        "runnable" : True,
        #TODO can this be handled like a timeSteppingScheme?
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "FunctionSpace::" ],
            [ "timeSteppingScheme" ]
        ]
    },


    "OperatorSplitting::Strang" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "timeSteppingScheme" ],
            [ "timeSteppingScheme" ]
        ]
    },
    "OperatorSplitting::Godunov" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "timeSteppingScheme" ],
            [ "timeSteppingScheme" ]
        ]
    },


    "CellmlAdapter" : {
        "discretizableInTime" : True,
        "template_arguments" : [
            [ "Integer" ],
            [ "Integer" ],
            [ "FunctionSpace::" ]
        ]
    },


    "FunctionSpace::FunctionSpace" : {
        "template_arguments" : [
            [ "Mesh::" ],
            [ "BasisFunction::" ]
        ]
    },


    "TimeSteppingScheme::ExplicitEuler" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "discretizableInTime" ]
        ]
    },
    "TimeSteppingScheme::ImplicitEuler" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "discretizableInTime" ]
        ]
    },
    "TimeSteppingScheme::Heun" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "discretizableInTime" ]
        ]
    },
    "TimeSteppingScheme::HeunAdaptive" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "discretizableInTime" ]
        ]
    },
    "TimeSteppingScheme::CrankNicolson" : {
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "discretizableInTime" ]
        ]
    },
    "TimeSteppingScheme::RepeatedCall" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            #TODO does this really accept any timeSteppingScheme
            [ "timeSteppingScheme" ]
        ]
    },
    #specalizedSolvers:
    "TimeSteppingScheme::StaticBidomainSolver" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "SpatialDiscretization::FiniteElementMethod" ],
            [ "SpatialDiscretization::FiniteElementMethod" ]
        ]
    },
    "TimeSteppingScheme::MultidomainSolver" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "SpatialDiscretization::FiniteElementMethod" ],
            [ "SpatialDiscretization::FiniteElementMethod" ]
        ]
    },
    "TimeSteppingScheme::MultidomainWithFatSolver" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "SpatialDiscretization::FiniteElementMethod" ],
            [ "SpatialDiscretization::FiniteElementMethod" ],
            [ "SpatialDiscretization::FiniteElementMethod" ]
        ]
    },



    "OutputWriter::OutputSurface" : {
        "runnable" : True,
        #TODO can this be handled like a timeSteppingScheme?
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "timeSteppingScheme", "SpatialDiscretization::" ]
        ]
    },


    "SpatialDiscretization::FiniteElementMethod" : {
        "runnable" : True,
        "discretizableInTime" : True,
        "template_arguments" : [
            [ "Mesh::" ],
            [ "BasisFunction::" ],
            [ "Quadrature::" ],
            [ "Equation::" ]
        ],
        "python_options" : {
            "prefactor" : {
                "description" : "prefactor",
                "type" : [ "double" ],
                "default" : "1.0"
            }
        }
    },


    "Mesh::StructuredRegularFixedOfDimension" : {
        "template_arguments" : [
            [ "1", "2", "3" ]
        ]
    },
    "Mesh::StructuredDeformableOfDimension" : {
        "template_arguments" : [
            [ "1", "2", "3" ]
        ]
    },
    "Mesh::UnstructuredDeformableOfDimension" : {
        "template_arguments" : [
            [ "1", "2", "3" ]
        ]
    },
    "Mesh::CompositeOfDimension" : {
        "template_arguments" : [
            [ "1", "2", "3" ]
        ]
    },


    "BasisFunction::CompletePolynomialOfDimensionAndOrder" : {
        "template_arguments" : [
            [ "1", "2", "3" ],
            [ "0", "1", "2" ]
        ]
    },
    "BasisFunction::Hermite" : {},
    "BasisFunction::LagrangeOfOrder" : {
        "template_arguments_needed" : 0,
        "template_arguments" : [
            [ "1", "2" ]
        ]
    },
    # TODO are there BasisFunction::Mixed?


    "Quadrature::None" : {},
    "Quadrature::ClenshawCurtis" : {
        "template_arguments" : [
            [ "1", "2", "3", "4", "5", "6", "7", "64" ]
        ]
    },
    "Quadrature::Gauss" : {
        "template_arguments" : [
            [ "1" , "2" , "3", "4", "5", "6", "7", "8", "10", "12", "16", "20", "24", "64" ]
        ]
    },
    "Quadrature::NewtonCotes" : {
        "template_arguments" : [
            [ "1", "2", "3", "4", "5", "6", "7", "8" ]
        ]
    },
    "Quadrature::TensorProduct" : {
        "template_arguments" : [
            [ "1", "2", "3" ],
            [ "Quadrature::" ]
        ]
    },
    # TODO are there Quadrature::Mixed?
    #"Quadrature::Mixed" : {
    #    "template_arguments" : [
    #       [ ],
    #       [ "Quadrature::ClenshawCurtis", "Quadrature::Gauss", "Quadrature::NewtonCotes" ]
    #    ]
    #},


    "Equation::Dynamic::IsotropicDiffusion" : {},
    "Equation::Dynamic::AnisotropicDiffusion" : {},
    "Equation::Dynamic::DirectionalDiffusion" : {},
    "Equation::Static::Laplace" : {},
    "Equation::Static::GeneralizedLaplace" : {},
    "Equation::Static::LinearElasticity" : {},
    "Equation::Static::LinearElasticityActiveStress" : {},
    #TODO are these correct?
    "Equation::SolidMechanics::MooneyRivlinIncompressible3D" : {},
    "Equation::SolidMechanics::TransverselyIsotropicMooneyRivlinIncompressible3D" : {},
    "Equation::SolidMechanics::TransverselyIsotropicMooneyRivlinIncompressibleActive3D" : {},
    "Equation::SolidMechanics::HyperelasticTendon" : {},
    "Equation::SolidMechanics::HyperelasticityBase" : {},
    "Equation::Static::Poisson" : {},
    "Equation::Static::GeneralizedPoisson" : {},
}

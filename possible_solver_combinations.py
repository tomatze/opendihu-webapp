# each dict entry corresponds to a cpp-class 
# each class-dict can have a ordered list with template_arguments (assuming no args if omitted)

# possible outer structures (runnables) have the key runnable set to True (assuming False if ommited)

# structures that are discretizable in time have discretizableInTime set to True (assuming False if ommited)
# "discretizableInTime" in template_arguments will get expanded to all classes, which are discretizableInTime

# the keyword "Integer" can be used in template_arguments where an integer is expected (e.g. in CellmlAdapter)

# lists of the form [ "Mesh::" ] get auto expanded to [ "Mesh::StructuredRegularFixedOfDimension", "Mesh::Str..", ... ]

# classes added so far:
# TODO specalizedSolvers
# TODO operatorsplitting
# TODO postprocessing
# CellmlAdapter
# FunctionSpace::
# OutputWriter::
# TimeSteppingScheme::
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
            #TODO meta
        }
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
        "template_arguments" : [
            [ "discretizableInTime" ]
        ]
    },

    "TimeSteppingScheme::ImplicitEuler" : {
        "template_arguments" : [
            [ "discretizableInTime" ]
        ]
    },

    "TimeSteppingScheme::Heun" : {
        "runnable" : True,
        "template_arguments" : [
            [ "discretizableInTime" ]
        ]
    },

    "TimeSteppingScheme::HeunAdaptive" : {
        "runnable" : True,
        "template_arguments" : [
            [ "discretizableInTime" ]
        ]
    },

    "TimeSteppingScheme::CrankNicolson" : {
        "template_arguments" : [
            [ "discretizableInTime" ]
        ]
    },


    "OutputWriter::OutputSurface" : {
        "runnable" : True,
        "template_arguments" : [
            [ "SpatialDiscretization::" ]
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


    "BasisFunction::CompletePolynomialOfDimensionAndOrder" : {
        "template_arguments" : [
            [ "1", "2", "3" ],
            [ "0", "1", "2" ]
        ]
    },
    "BasisFunction::Hermite" : {},
    "BasisFunction::LagrangeOfOrder" : {
        "template_arguments" : [
            [ "0", "1" ]
        ]
    },
    #"BasisFunction::Mixed" : [
    #    [ "LowOrderBasisFunction" ],
    #    [ "HighOrderBasisFunction" ]
    #],
    #"LowOrderBasisFunction" : [],
    #"HighOrderBasisFunction" : [],


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
    #"Quadrature::Mixed" : [
    #    [ "LowOrderQuadrature" ],
    #    [ "HighOrderQuadrature" ]
    #],
    #"LowOrderQuadrature" : [],
    #"HighOrderQuadrature" : [
    #    [
    #        "Quadrature::ClenshawCurtis",
    #        "Quadrature::Gauss",
    #        "Quadrature::NewtonCotes"
    #    ]
    #],


    "Equation::Dynamic::IsotropicDiffusion" : {},
    "Equation::Dynamic::AnisotropicDiffusion" : {},
    "Equation::Static::Laplace" : {},
    "Equation::Static::GeneralizedLaplace" : {},
    "Equation::Static::LinearElasticity" : {},
    "Equation::Static::LinearElasticityActiveStress" : {},
    #TODO are these correct?
    "Equation::SolidMechanics::MooneyRivlinIncompressible3D" : {},
    "Equation::SolidMechanics::TransverselyIsotropicMooneyRivlinIncompressible3D" : {},
    "Equation::SolidMechanics::TransverselyIsotropicMooneyRivlinIncompressibleActive3D" : {},
    "Equation::SolidMechanics::HyperelasticTendon" : {},
    "Equation::Static::Poisson" : {},
    "Equation::Static::GeneralizedPoisson" : {},
}

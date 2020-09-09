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
# Postprocessing::ParallelFiberEstimation
# Postprocessing::StreamlineTracer
# PreciceAdapter::ContractionDirichletBoundaryConditions
# PreciceAdapter::ContractionNeumannBoundaryConditions
# PreciceAdapter::PartitionedFibers
# PreciceAdapter::MuscleContraction
# MuscleContractionSolver
# FastMonodomainSolver
# SpatialDiscretization::HyperelasticitySolver
# Control::MultipleInstances
# Control::Coupling
# TODO Control::MultipleCoupling
# Control::LoadBalancing
# Control::MapDofs
# OperatorSplitting::
# CellmlAdapter
# ModelOrderReduction::POD
# ModelOrderReduction::LinearPart
# ModelOrderReduction::ExplicitEulerReduced
# ModelOrderReduction::ImplicitEulerReduced
# FunctionSpace::
# OutputWriter::OutputSurface
# TODO add other OutputWriters
# PrescribedValues
# TimeSteppingScheme::
# TimeSteppingScheme::DynamicHyperelasticitySolver
# TimeSteppingScheme::StaticBidomainSolver
# TimeSteppingScheme::MultidomainSolver
# TimeSteppingScheme::MultidomainWithFatSolver
# TimeSteppingScheme::QuasiStaticNonlinearElasticitySolverFebio
# TimeSteppingScheme::NonlinearElasticitySolverFebio
# TimeSteppingScheme::QuasiStaticLinearElasticitySolver
# TimeSteppingScheme::QuasiStaticNonlinearElasticitySolverChaste
# SpatialDiscretization::FiniteElementMethod
# Mesh::
# BasisFunction::
# Quadrature::
# Equation::
possible_solver_combinations = {
    "GLOBAL" : {
        "python_options" : {
            "scenarioName" : "test-scenario",
            "logFormat" : "csv", # csv or json
            "solverStructureDiagramFile" : "solver_structure.txt",
            "Meshes" : {},
            "mappingsBetweenMeshesLogFile" : "mappings_between_meshes.txt",
            "MappingsBetweenMeshes" : {},
            "Solvers" : {},
            #TODO add meta
            "meta" : {}
            ### CHILD ###
        }
    },


    "Postprocessing::ParallelFiberEstimation" : {
        "runnable" : True,
        "template_arguments" : [
            [ "BasisFunction::" ]
        ]
    },
    "Postprocessing::StreamlineTracer" : {
        "runnable" : True,
        "template_arguments" : [
            [ "discretizableInTime" ]
        ]
    },


    "PreciceAdapter::ContractionDirichletBoundaryConditions" : {
        "runnable" : True,
        "template_arguments" : [
            [ "timeSteppingScheme" ]
        ]
    },
    "PreciceAdapter::ContractionNeumannBoundaryConditions" : {
        "runnable" : True,
        "template_arguments" : [
            [ "timeSteppingScheme" ]
        ]
    },
    "PreciceAdapter::PartitionedFibers" : {
        "runnable" : True,
        "template_arguments" : [
            [ "timeSteppingScheme" ]
        ]
    },
    "PreciceAdapter::MuscleContraction" : {
        "runnable" : True,
        "template_arguments" : [
            [ "MuscleContractionSolver" ]
        ]
    },
    "MuscleContractionSolver" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments_needed" : 0,
        "template_arguments" : [
            # TODO this should only accept Mesh::StructuredDeformableOfDimension<3>
            # and maybe Mesh::CompositeOfDimension<3>?
            [ "Mesh::" ]
        ]
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
    "SpatialDiscretization::HyperelasticitySolver" : {
        "runnable" : True,
        #TODO can this be handled like a timeSteppingScheme?
        "timeSteppingScheme" : True,
        "template_arguments_needed" : 0,
        "template_arguments" : [
            [ "Equation::SolidMechanics::TransverselyIsotropicMooneyRivlinIncompressible3D" ]
            # TODO can this handle more template_arguments?
        ]
    },


    "Control::MultipleInstances" : {
        "runnable" : True,
        #TODO can this be handled like a timeSteppingScheme?
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "timeSteppingScheme" ]
        ],
        "python_options" : {
            "MultipleInstances": {
                "nInstances": 1,
                "instances": [],
            }
        }
    },
    "Control::Coupling" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "timeSteppingScheme" ],
            [ "timeSteppingScheme" ]
        ]
    },
    "Control::LoadBalancing" : {
        # TODO is this runnable
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
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
        ],
        "python_options" : {
            #TODO
            "StrangSplitting" : {
                "timeStepWidth" : 1e-1,
                "Term1" : {
                    ### CHILD ###
                },
                "Term2" : {
                    ### CHILD ###
                }
            },
        }
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
        "template_arguments_needed" : 1,
        "template_arguments" : [
            [ "Integer" ],
            [ "Integer" ],
            [ "FunctionSpace::" ]
        ]
    },


    "ModelOrderReduction::POD" : {
        "discretizableInTime" : True,
        "template_arguments" : [
            [ "discretizableInTime" ],
            [ "ModelOrderReduction::LinearPart" ]
        ]
    },
    "ModelOrderReduction::LinearPart" : {},
    "ModelOrderReduction::ExplicitEulerReduced" : {
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "TimeSteppingScheme::ExplicitEuler" ]
        ]
    },
    "ModelOrderReduction::ImplicitEulerReduced" : {
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "TimeSteppingScheme::ImplicitEuler" ]
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
    "TimeSteppingScheme::RepeatedCallStatic" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "SpatialDiscretization::FiniteElementMethod" ]
        ]
    },
    #specalizedSolvers:
    "TimeSteppingScheme::DynamicHyperelasticitySolver" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments_needed" : 0,
        "template_arguments" : [
            [ "Equation::" ],
            # TODO this should only accept Mesh::StructuredDeformableOfDimension<3>
            [ "Mesh::StructuredRegularFixedOfDimension" ]
        ]
    },
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
        ],
        "python_options" : {
            "MultidomainSolver" : "test",
        }
    },
    "TimeSteppingScheme::QuasiStaticNonlinearElasticitySolverFebio" : {
        "runnable" : True,
        "timeSteppingScheme" : True
    },
    "TimeSteppingScheme::NonlinearElasticitySolverFebio" : {
        "runnable" : True,
        "timeSteppingScheme" : True
    },
    "TimeSteppingScheme::QuasiStaticLinearElasticitySolver" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "SpatialDiscretization::FiniteElementMethod" ]
        ]
    },
    "TimeSteppingScheme::QuasiStaticNonlinearElasticitySolverChaste" : {
        "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "Integer" ]
        ]
    },


    "PrescribedValues" : { "runnable" : True,
        "timeSteppingScheme" : True,
        "template_arguments_needed" : 1,
        "template_arguments" : [
            [ "FunctionSpace::FunctionSpace" ],
            [ "1", "2", "3" ],
            [ "1", "2", "3" ]
        ]
    },



    "OutputWriter::OutputSurface" : {
        "runnable" : True,
        #TODO can this be handled like a timeSteppingScheme?
        "timeSteppingScheme" : True,
        "template_arguments" : [
            [ "timeSteppingScheme", "SpatialDiscretization::FiniteElementMethod" ]
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
            "FiniteElementMethod" : {
                "prefactor" : 1.0, # this is the prefactor
                "rightHandSide" : {},
                "inputMeshIsGlobal" : True,
                ### CHILD ###
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

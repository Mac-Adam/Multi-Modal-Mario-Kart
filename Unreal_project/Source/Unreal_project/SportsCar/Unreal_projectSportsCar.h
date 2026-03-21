// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Unreal_projectPawn.h"
#include "Unreal_projectSportsCar.generated.h"

/**
 *  Sports car wheeled vehicle implementation
 */
UCLASS(abstract)
class AUnreal_projectSportsCar : public AUnreal_projectPawn
{
	GENERATED_BODY()
	
public:

	AUnreal_projectSportsCar();
};

/* This file is part of the FaCT++ DL reasoner
Copyright (C) 2013 by Dmitry Tsarkov

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
*/

// incremental reasoning implementation

#include "Kernel.h"
#include "OntologyBasedModularizer.h"
#include "Actor.h"
#include "tOntologyPrinterLISP.h"
#include "procTimer.h"
#include "IncrementalClassifier.h"

TsProcTimer moduleTimer, subCheckTimer;
int nModule = 0;
IncrementalClassifier* Classifier = NULL;
ReasoningKernel* Reasoner = new ReasoningKernel();
TSignature OldSig;

/// setup Name2Sig for a given name C
AxiomVec
ReasoningKernel :: setupSig ( const ClassifiableEntry* C )
{
	AxiomVec ret;

	moduleTimer.Start();
	// get the entity; do nothing if doesn't exist
	const TNamedEntity* entity = C->getEntity();
	if ( entity == NULL )
		return ret;

	// prepare a place to update
	TSignature sig;
	NameSigMap::iterator insert = Name2Sig.find(C->getName());
	if ( insert == Name2Sig.end() )
		insert = Name2Sig.insert(std::make_pair(C->getName(),&sig)).first;
	else
		delete insert->second;

	// calculate a module
	sig.add(entity);
	ret = getModExtractor(false)->getModule(sig,M_BOT);
	++nModule;

	// perform update
	insert->second = new TSignature(getModExtractor(false)->getModularizer()->getSignature());

	moduleTimer.Stop();

	return ret;
}

/// initialise the incremental bits on full reload
void
ReasoningKernel :: initIncremental ( void )
{
	delete ModSyn;
	ModSyn = NULL;
	// fill the module signatures of the concepts
	for ( TBox::c_const_iterator p = getTBox()->c_begin(), p_end = getTBox()->c_end(); p != p_end; ++p )
		setupSig(*p);

	getTBox()->setNameSigMap(&Name2Sig);
	// fill in ontology signature
	OntoSig = Ontology.getSignature();
	std::cout << "Init modules (" << nModule << ") time: " << moduleTimer << std::endl;
}

void
ReasoningKernel :: doIncremental ( void )
{
	std::cout << "Incremental!\n";
	// re-set the modularizer to use updated ontology
	delete ModSyn;
	ModSyn = NULL;
	delete Reasoner;
	Reasoner = new ReasoningKernel();
	OldSig = TSignature();

	std::set<std::string> MPlus, MMinus;
	std::set<const TNamedEntry*> excluded;

	// detect new- and old- signature elements
	TSignature NewSig = Ontology.getSignature();
	TSignature::BaseType RemovedEntities, AddedEntities;
	std::set_difference(OntoSig.begin(), OntoSig.end(), NewSig.begin(), NewSig.end(), inserter(RemovedEntities, RemovedEntities.begin()));
	std::set_difference(NewSig.begin(), NewSig.end(), OntoSig.begin(), OntoSig.end(), inserter(AddedEntities, AddedEntities.begin()));

	Taxonomy* tax = getCTaxonomy();
//	std::cout << "Original Taxonomy:";
//	tax->print(std::cout);

	// deal with removed concepts
	TSignature::BaseType::iterator e, e_end;
	for ( e = RemovedEntities.begin(), e_end = RemovedEntities.end(); e != e_end; ++e )
		if ( const TConcept* C = dynamic_cast<const TConcept*>((*e)->getEntry()) )
		{
			excluded.insert(C);
			// remove all links
			C->getTaxVertex()->remove();
			// update Name2Sig
			delete Name2Sig[C->getName()];
			Name2Sig.erase(C->getName());
		}

	// deal with added concepts
	tax->deFinalise();
	for ( e = AddedEntities.begin(), e_end = AddedEntities.end(); e != e_end; ++e )
		if ( const TDLConceptName* cName = dynamic_cast<const TDLConceptName*>(*e) )
		{
			// register the name in TBox
			TreeDeleter TD(this->e(cName));
			TConcept* C = dynamic_cast<TConcept*>(cName->getEntry());
			// create sig for it
			setupSig(C);
			// init the taxonomy element
			TaxonomyVertex* cur = tax->getCurrent();
			cur->clear();
			cur->setSample(C);
			cur->addNeighbour ( /*upDirection=*/true, tax->getTopVertex() );
			tax->finishCurrentNode();
			std::cout << "Insert " << C->getName() << std::endl;
		}
	OntoSig = NewSig;

	// fill in M^+ and M^- sets
	TsProcTimer t;
	t.Start();
	LocalityChecker* lc = getModExtractor(false)->getModularizer()->getLocalityChecker();
	TOntology::iterator p, nb = Ontology.beginUnprocessed(), ne = Ontology.end(), rb = Ontology.beginRetracted(), re = Ontology.endRetracted();
//	TLISPOntologyPrinter pr(std::cout);
//	for ( p = nb; p != ne; ++p )
//	{
//		std::cout << "Add:";
//		(*p)->accept(pr);
//	}
//	for ( p = rb; p != re; ++p )
//	{
//		std::cout << "Del:";
//		(*p)->accept(pr);
//	}
	// TODO: add new sig here
	for ( NameSigMap::iterator p = Name2Sig.begin(), p_end = Name2Sig.end(); p != p_end; ++p )
	{
		lc->setSignatureValue(*p->second);
		for ( TOntology::iterator notProcessed = nb; notProcessed != ne; ++notProcessed )
			if ( !lc->local(*notProcessed) )
			{
				MPlus.insert(p->first);
//				std::cout << "Non-local NP axiom ";
//				(*notProcessed)->accept(pr);
//				std::cout << " wrt " << p->first->getName() << std::endl;
				break;
			}
		for ( TOntology::iterator retracted = rb; retracted != re; retracted++ )
			if ( !lc->local(*retracted) )
			{
				MMinus.insert(p->first);
				// FIXME!! only concepts for now
				TaxonomyVertex* v = pTBox->getConcept(p->first)->getTaxVertex();
				if ( v->noNeighbours(true) )
				{
					v->addNeighbour(true,tax->getTopVertex());
					tax->getTopVertex()->addNeighbour(false,v);
				}
//				std::cout << "Non-local RT axiom ";
//				(*retracted)->accept(pr);
//				std::cout << " wrt " << p->first->getName() << std::endl;
				break;
			}
	}
	t.Stop();

	tax->finalise();
//	std::cout << "Adjusted Taxonomy:";
//	tax->print(std::cout);

	const char* filename = "incremental.tax";
	// save taxonomy
	std::ofstream o(filename);
	getTBox()->SaveTaxonomy(o,excluded);
	o.close();

	// do actual change
	useIncremenmtalReasoning = false;
	forceReload();
	pTBox->isConsistent();
	useIncremenmtalReasoning = true;

	// load the taxonomy
	std::ifstream i(filename);
	getTBox()->LoadTaxonomy(i);

	tax = getCTaxonomy();
//	std::cout << "Reloaded Taxonomy:";
//	tax->print(std::cout);
//	std::cout.flush();

	tax->deFinalise();

	// fill in an order to
	std::queue<TaxonomyVertex*> queue;
	std::vector<const ClassifiableEntry*> toProcess;
	queue.push(tax->getTopVertex());
	while ( !queue.empty() )
	{
		TaxonomyVertex* cur = queue.front();
		queue.pop();
		if ( tax->isVisited(cur) )
			continue;
		tax->setVisited(cur);
		const ClassifiableEntry* entry = cur->getPrimer();
		if ( MPlus.find(entry->getName()) != MPlus.end() || MMinus.find(entry->getName()) != MMinus.end() )
			toProcess.push_back(entry);
		for ( TaxonomyVertex::iterator p = cur->begin(/*upDirection=*/false), p_end = cur->end(/*upDirection=*/false); p != p_end; ++p )
			queue.push(*p);
	}
	tax->clearVisited();
	std::cout << "Determine concepts that need reclassification (" << toProcess.size() << "): done in " << t << std::endl;

//	std::cout << "Add/Del names Taxonomy:\n";
//	tax->print(std::cout);

//	Classifier = new IncrementalClassifier(tax);
	std::set<const ClassifiableEntry*> Processed;
	for ( std::vector<const ClassifiableEntry*>::iterator p = toProcess.begin(), p_end = toProcess.end(); p != p_end; ++p )
		if ( Processed.count(*p) == 0 )
		{
			reclassifyNode ( *p, MPlus.find((*p)->getName()) != MPlus.end(), MMinus.find((*p)->getName()) != MMinus.end() );
//			tax->print(std::cout);
//			std::cout.flush();
			for ( std::vector<const ClassifiableEntry*>::iterator q = p+1; q != p_end; ++q )
				if ( Processed.count(*q) == 0 && OldSig.contains((*q)->getEntity()) )	// same module
				{
					reclassifyNode ( *q, MPlus.find((*q)->getName()) != MPlus.end(), MMinus.find((*q)->getName()) != MMinus.end() );
//					tax->print(std::cout);
//					std::cout.flush();
					Processed.insert(*q);
				}
		}

//	for ( std::set<const ClassifiableEntry*>::iterator p = MAll.begin(), p_end = MAll.end(); p != p_end; ++p )
//	{
//		reclassifyNode ( (*p)->getTaxVertex(), MPlus.find(*p) != MPlus.end(), MMinus.find(*p) != MMinus.end() );
////		tax->print(std::cout);
//		std::cout.flush();
//	}
	tax->finalise();
//			tax->print(std::cout);
//			std::cout.flush();
	Ontology.setProcessed();
	std::cout << "Total modularization (" << nModule << ") time: " << moduleTimer << "\nTotal reasoning time: " << subCheckTimer << std::endl;
}

static std::ostream& operator << ( std::ostream& o, const TSignature& sig )
{
	o << "[";
	for ( TSignature::iterator p = sig.begin(), p_end = sig.end(); p != p_end; ++p )
		o << (*p)->getName() << " ";
	o << "]" << std::endl;
	return o;
}

/// reclassify (incrementally) NODE wrt ADDED or REMOVED flags
void
ReasoningKernel :: reclassifyNode ( const ClassifiableEntry* entry, bool added, bool removed )
{
	TaxonomyVertex* node = entry->getTaxVertex();
	std::cout << "Reclassify " << entry->getName() << " (" << (added?"Added":"") << (removed?" Removed":"") << ")" << std::endl;

	TsProcTimer timer;
	timer.Start();
	// update Name2Sig
	AxiomVec Module = setupSig(entry);
	const TSignature ModSig = getModExtractor(false)->getModularizer()->getSignature();
	timer.Stop();
	std::cout << "Creating module (" << Module.size() << " axioms) time: " << timer;// << " sig: " << ModSig << " old: " << OldSig;
	timer.Reset();

	// save all signature-2-entry map
//	std::map<const TNamedEntity*, TNamedEntry*> KeepMap;
//	TSignature::iterator s, s_end = ModSig.end();
//	for ( s = ModSig.begin(); s != s_end; s++ )
//	{
//		const TNamedEntity* entity = *s;
//		KeepMap[entity] = entity->getEntry();
//		const_cast<TNamedEntity*>(entity)->setEntry(NULL);
//	}

	timer.Start();
//	if ( !(ModSig <= OldSig) )	// create new reasoner
//	{
//		// save signature
//		OldSig = ModSig;
//
//		// init the reasoner
//		delete Reasoner;
//		Reasoner = new ReasoningKernel();
//		Reasoner->setUseIncremenmtalReasoning(false);
//
//		TOntology& ontology = Reasoner->getOntology();
////		std::cout << "Module: \n";
////		TLISPOntologyPrinter pr(std::cout);
//		for ( AxiomVec::iterator p = Module.begin(), p_end = Module.end(); p != p_end; ++p )
//		{
//			ontology.add(*p);
////			(*p)->accept(pr);
//		}
//		std::cout.flush();
//		Reasoner->isKBConsistent();
//		timer.Stop();
//		std::cout << "; init reasoner time: " << timer;
//
//		// clear an ontology in a safe way
//		Reasoner->getOntology().safeClear();
//	}
//
	timer.Reset();
	timer.Start();
	subCheckTimer.Start();
#if 0
	// update top links
	node->removeLinks(/*upDirection=*/true);
	Actor actor;
	actor.needConcepts();
	subCheckTimer.Start();
	Reasoner->getSupConcepts ( static_cast<const TDLConceptName*>(entry->getEntity()), /*direct=*/true, actor );
	subCheckTimer.Stop();
	Actor::Array2D parents;
	actor.getFoundData(parents);
	for ( Actor::Array2D::iterator q = parents.begin(), q_end = parents.end(); q != q_end; ++q )
	{
		const ClassifiableEntry* parentCE = *q->begin();
		if ( parentCE == Reasoner->getCTaxonomy()->getTopVertex()->getPrimer() )	// special case it
		{	// FIXME!! re-think after a proper taxonomy change
			node->addNeighbour ( /*upDirection=*/true, getCTaxonomy()->getTopVertex() );
			break;
		}
//		std::cout << "Set parent " << parentCE->getName() << std::endl;
		node->addNeighbour ( /*upDirection=*/true, getTBox()->getConcept(parentCE->getName())->getTaxVertex() );
	}
	// actually add node
	node->incorporate();
#elif 0
	Classifier->reclassify ( node, Reasoner, &ModSig, added, removed );
#elif 1
	getTBox()->reclassify ( node, &ModSig, added, removed );
#endif
	subCheckTimer.Stop();
	timer.Stop();
	std::cout << "; reclassification time: " << timer << std::endl;

	// restore all signature-2-entry map
//	for ( s = ModSig.begin(); s != s_end; s++ )
//		const_cast<TNamedEntity*>(*s)->setEntry(KeepMap[*s]);
}